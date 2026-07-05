"""예시 쿼리를 실행해 examples/example_runs.md를 생성한다.

두 가지 모드:
  - full: LLM 키가 있으면 run_agent()로 실제 에이전트가 도구를 오케스트레이션한다(실서비스 경로).
  - scripted: 키가 없으면, 에이전트가 선택할 도구 호출 시퀀스를 사람이 스크립트로 재현한다.
    데이터·집계·조립은 실제 코드(실제 CT.gov API)로 수행되며, 오직 "도구 선택/순서"만 사람이
    대신 정한다. example_runs.md에 생성 모드를 표기한다.

사용:
  PYTHONPATH=. uv run python scripts/run_examples.py
"""

import json
from pathlib import Path

from app.agent.runner import assemble_response, run_agent
from app.agent.session import Session
from app.agent.tools import make_tools
from app.config import settings

# 각 예시: (설명, 요청 payload, 에이전트가 밟을 것으로 기대되는 도구 시퀀스 함수)
# 도구 시퀀스 함수는 make_tools로 만든 tools dict를 받아 실행한다.


def seq_time_trend(t):
    t["search_trials"].invoke({"drug_name": "Pembrolizumab", "start_year": 2015})
    t["aggregate_by"].invoke({"field": "year"})
    t["finalize_visualization"].invoke(
        {"artifact_id": "time_trend_1", "chart_type": "time_series", "title": "Pembrolizumab trials over time (since 2015)"}
    )


def seq_distribution(t):
    t["search_trials"].invoke({"condition": "diabetes"})
    t["aggregate_by"].invoke({"field": "phase"})
    t["finalize_visualization"].invoke(
        {"artifact_id": "distribution_1", "chart_type": "bar_chart", "title": "Diabetes trials by phase"}
    )


def seq_comparison(t):
    t["search_trials"].invoke({"label": "pembro", "drug_name": "Pembrolizumab"})
    t["search_trials"].invoke({"label": "nivo", "drug_name": "Nivolumab"})
    t["compare_groups"].invoke({"search_labels": ["pembro", "nivo"], "field": "phase"})
    t["finalize_visualization"].invoke(
        {"artifact_id": "comparison_1", "chart_type": "grouped_bar_chart", "title": "Pembrolizumab vs Nivolumab by phase"}
    )


def seq_geo(t):
    t["search_trials"].invoke({"condition": "breast cancer", "overall_status": "RECRUITING"})
    t["aggregate_by"].invoke({"field": "country"})
    t["finalize_visualization"].invoke(
        {"artifact_id": "geo_1", "chart_type": "bar_chart", "title": "Recruiting breast cancer trials by country"}
    )


def seq_network(t):
    t["search_trials"].invoke({"condition": "melanoma"})
    t["build_network"].invoke({"dimension": "sponsor_drug"})
    t["finalize_visualization"].invoke(
        {"artifact_id": "network_1", "chart_type": "network_graph", "title": "Sponsor–drug network for melanoma"}
    )


def seq_empty(t):
    t["search_trials"].invoke({"drug_name": "Zzzznonexistentdrug"})
    # 0건이면 에이전트는 집계/finalize 없이 종료 → no_data 응답


EXAMPLES = [
    ("Time trend — 특정 약물의 연도별 시험 수", {"query": "How has the number of Pembrolizumab trials changed per year since 2015?"}, seq_time_trend),
    ("Distribution — 질환의 phase별 분포", {"query": "How are diabetes trials distributed across phases?", "condition": "diabetes"}, seq_distribution),
    ("Comparison — 두 약물의 phase 비교", {"query": "Compare trial phases for Pembrolizumab vs Nivolumab."}, seq_comparison),
    ("Geographic — 국가별 모집중 시험 수", {"query": "Which countries have the most recruiting trials for breast cancer?", "condition": "breast cancer"}, seq_geo),
    ("Network — 질환의 sponsor↔drug 관계망", {"query": "Show a network of sponsors and drugs for melanoma trials.", "condition": "melanoma"}, seq_network),
    ("Empty result — 존재하지 않는 약물(graceful handling)", {"query": "How are trials for Zzzznonexistentdrug distributed across phases?"}, seq_empty),
]


def run_scripted(payload: dict, seq) -> dict:
    session = Session(input_filters={k: v for k, v in payload.items() if k != "query"})
    tools = {t.name: t for t in make_tools(session)}
    seq(tools)
    return assemble_response(session)


def main() -> None:
    has_key = bool(settings.anthropic_api_key or settings.openai_api_key)
    mode = "full (실제 react agent가 도구 오케스트레이션)" if has_key else "scripted (도구 시퀀스 재현, 데이터·집계는 실제 API/코드)"

    lines = [
        "# 예시 실행 결과 (Example Runs)",
        "",
        f"> 생성 모드: **{mode}**",
        "> 모든 `data`/`citations` 값은 ClinicalTrials.gov v2 API의 실제 응답을 결정론적 도구가 집계한 것입니다.",
        "> `scripted` 모드에서는 에이전트가 런타임에 선택할 **도구 호출 순서만** 사람이 재현했고,"
        " 검색·집계·조립은 실제 코드가 그대로 실행했습니다(수치는 LLM을 거치지 않음).",
        "",
    ]

    for title, payload, seq in EXAMPLES:
        print(f"running: {title}")
        try:
            result = run_agent(payload["query"], {k: v for k, v in payload.items() if k != "query"}) if has_key else run_scripted(payload, seq)
        except Exception as e:  # noqa: BLE001
            result = {"error": f"{type(e).__name__}: {e}"}

        lines += [
            f"## {title}", "",
            "**요청:**", "```json", json.dumps(payload, ensure_ascii=False, indent=2), "```", "",
            "**응답:**", "```json", json.dumps(result, ensure_ascii=False, indent=2), "```", "",
        ]

    out = Path(__file__).parent.parent / "examples" / "example_runs.md"
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"\nwrote {out}")


if __name__ == "__main__":
    main()
