"""예시 쿼리를 실행해 examples/example_runs.md를 생성한다.

두 가지 모드:
  - 전체(full): LLM 키가 있으면 intent 노드까지 포함한 전체 그래프를 실행한다(실서비스 경로).
  - 주입(injected): 키가 없으면 intent만 손으로 주입하고 나머지 노드(실제 CT.gov 조회·집계·
    스펙 조립)는 그대로 실행한다. 데이터는 실제 API에서 온 진짜 값이며, 오직 자연어→intent
    해석 단계만 대체된다. example_runs.md에 어떤 모드로 생성됐는지 표기한다.

사용:
  uv run python scripts/run_examples.py
"""

import json
from pathlib import Path

from app.config import settings
from app.graph.nodes.aggregate import aggregate_node
from app.graph.nodes.chart_select import chart_select_node
from app.graph.nodes.comparison import comparison_node
from app.graph.nodes.fetch import fetch_node
from app.graph.nodes.query_builder import query_builder_node
from app.graph.nodes.spec_builder import spec_builder_node
from app.graph.state import ComparisonGroup, Intent

# (설명, 요청 payload, 해당 요청에 대해 파서가 만들 것으로 기대되는 Intent)
EXAMPLES = [
    (
        "Time trend — 특정 약물의 연도별 시험 수",
        {"query": "How has the number of Pembrolizumab trials changed per year since 2015?"},
        Intent(drug_name="Pembrolizumab", start_year=2015, analysis_type="time_trend"),
    ),
    (
        "Distribution — 질환의 phase별 분포",
        {"query": "How are diabetes trials distributed across phases?", "condition": "diabetes"},
        Intent(condition="diabetes", analysis_type="distribution", distribution_field="phase"),
    ),
    (
        "Comparison — 두 약물의 phase 비교",
        {"query": "Compare trial phases for Pembrolizumab vs Nivolumab."},
        Intent(
            analysis_type="comparison",
            comparison_groups=[
                ComparisonGroup(label="Pembrolizumab", drug_name="Pembrolizumab"),
                ComparisonGroup(label="Nivolumab", drug_name="Nivolumab"),
            ],
        ),
    ),
    (
        "Geographic — 국가별 모집중 시험 수",
        {"query": "Which countries have the most recruiting trials for breast cancer?", "condition": "breast cancer"},
        Intent(condition="breast cancer", overall_status="RECRUITING", analysis_type="geo"),
    ),
    (
        "Network — 질환의 sponsor↔drug 관계망",
        {"query": "Show a network of sponsors and drugs for melanoma trials.", "condition": "melanoma"},
        Intent(condition="melanoma", analysis_type="network", network_dimension="sponsor_drug"),
    ),
    (
        "Empty result — 존재하지 않는 약물(graceful handling)",
        {"query": "How are trials for Zzzznonexistentdrug distributed across phases?"},
        Intent(drug_name="Zzzznonexistentdrug", analysis_type="distribution", distribution_field="phase"),
    ),
]


def run_injected(payload: dict, intent: Intent) -> dict:
    """intent를 주입하고 나머지 실제 노드를 순서대로 실행."""
    state: dict = {
        "query": payload["query"],
        "input_filters": {k: v for k, v in payload.items() if k != "query"},
        "intent": intent,
    }
    if intent.analysis_type == "comparison":
        state.update(comparison_node(state))
    else:
        state.update(query_builder_node(state))
        state.update(fetch_node(state))
        state.update(aggregate_node(state))
    state.update(chart_select_node(state))
    state.update(spec_builder_node(state))
    return {
        "visualization": state["visualization"],
        "meta": state["meta"],
        "citations": state.get("citations"),
    }


def run_full(payload: dict) -> dict:
    from app.graph.build import compiled_graph

    result = compiled_graph.invoke(
        {"query": payload["query"], "input_filters": {k: v for k, v in payload.items() if k != "query"}}
    )
    return {
        "visualization": result["visualization"],
        "meta": result["meta"],
        "citations": result.get("citations"),
    }


def main() -> None:
    has_key = bool(settings.anthropic_api_key or settings.openai_api_key)
    mode = "full (LLM 포함 전체 그래프)" if has_key else "injected (intent 주입, 데이터는 실제 API)"

    lines = [
        "# 예시 실행 결과 (Example Runs)",
        "",
        f"> 생성 모드: **{mode}**",
        "> 모든 `data`/`citations` 값은 ClinicalTrials.gov v2 API의 실제 응답에서 집계된 것입니다.",
        f"> `injected` 모드에서는 자연어→intent 해석 단계만 사람이 대체했고, 나머지 파이프라인"
        f" (쿼리 생성·API 조회·집계·차트 선택·스펙 조립)은 실제 코드가 그대로 실행했습니다.",
        "",
    ]

    for title, payload, intent in EXAMPLES:
        print(f"running: {title}")
        try:
            result = run_full(payload) if has_key else run_injected(payload, intent)
        except Exception as e:  # noqa: BLE001
            result = {"error": f"{type(e).__name__}: {e}"}

        lines.append(f"## {title}")
        lines.append("")
        lines.append("**요청:**")
        lines.append("```json")
        lines.append(json.dumps(payload, ensure_ascii=False, indent=2))
        lines.append("```")
        lines.append("")
        lines.append("**응답:**")
        lines.append("```json")
        lines.append(json.dumps(result, ensure_ascii=False, indent=2))
        lines.append("```")
        lines.append("")

    out = Path(__file__).parent.parent / "examples" / "example_runs.md"
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"\nwrote {out}")


if __name__ == "__main__":
    main()
