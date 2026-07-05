"""에이전트 도구 세트.

설계 핵심:
- 도구는 모든 수치를 결정론적 코어(app/core)로 계산하고 결과를 Session에 저장한다.
- LLM에는 요약(preview)만 반환한다 → 토큰 절약 + LLM이 원시 숫자를 재생성/전사할 유인 제거.
- 최종 응답은 finalize가 지목한 artifact를 서버가 Session에서 직접 꺼내 만든다.

따라서 LLM은 "어떤 검색을 하고 어떤 집계를 조합할지"(오케스트레이션)만 통제하고,
"숫자가 얼마인지"는 절대 만들지 않는다.
"""

from langchain_core.tools import tool

from app.config import settings
from app.core.aggregate import (
    aggregate_comparison,
    aggregate_distribution,
    aggregate_geo,
    aggregate_network,
    aggregate_time_trend,
)
from app.core.query import build_ctgov_params
from app.agent.session import Artifact, SearchResult, Session
from app.services.ctgov_client import CtGovClient

FIELD_TO_KIND = {
    "year": "time_trend",
    "phase": "distribution",
    "intervention_type": "distribution",
    "status": "distribution",
    "country": "geo",
}

ALLOWED_CHART_TYPES = {
    "time_series",
    "bar_chart",
    "grouped_bar_chart",
    "network_graph",
    "no_data",
}

# artifact.kind 별로 finalize가 허용하는 chart_type 집합.
# LLM이 잘못된 조합을 확정하려 하면 finalize 도구가 거절(→ LLM 재시도 유도),
# 만에 하나 통과되어도 assemble_response의 안전벨트가 no_data로 강등한다.
KIND_TO_CHART: dict[str, set[str]] = {
    "time_trend":   {"time_series"},
    "distribution": {"bar_chart"},
    "comparison":   {"grouped_bar_chart"},
    "geo":          {"bar_chart"},
    "network":      {"network_graph"},
}


def make_tools(session: Session, client: CtGovClient | None = None) -> list:
    """주어진 Session에 바인딩된 도구 리스트를 만든다 (요청마다 새로 생성)."""
    client = client or CtGovClient()

    @tool
    def search_trials(
        label: str = "default",
        drug_name: str | None = None,
        condition: str | None = None,
        sponsor: str | None = None,
        country: str | None = None,
        trial_phase: str | None = None,
        start_year: int | None = None,
        end_year: int | None = None,
        overall_status: str | None = None,
    ) -> str:
        """ClinicalTrials.gov에서 조건에 맞는 임상시험을 검색해 결과 집합을 label로 저장한다.

        비교(comparison) 질문은 대상마다 label을 다르게 주어 여러 번 호출하라
        (예: label='drugA' 로 한 번, label='drugB' 로 한 번). 이후 집계 도구에서 이 label을 참조한다.

        Args:
            label: 이 검색 결과를 가리킬 이름. 단일 질문이면 'default'.
            drug_name: 약물/중재명 (브랜드명·동의어 가능).
            condition: 질환명.
            sponsor: 스폰서명.
            country: 국가명.
            trial_phase: PHASE1/PHASE2/PHASE3/PHASE4/EARLY_PHASE1/NA 중 하나.
            start_year: 시작 연도 하한.
            end_year: 시작 연도 상한.
            overall_status: RECRUITING/COMPLETED 등 모집 상태.
        Returns:
            검색된 시험 수와 cap 여부 요약.
        """
        # 요청에 명시된 필터는 LLM 인자보다 항상 우선한다(결정론적 보증).
        merged = {
            "drug_name": drug_name,
            "condition": condition,
            "sponsor": sponsor,
            "country": country,
            "trial_phase": trial_phase,
            "start_year": start_year,
            "end_year": end_year,
            "overall_status": overall_status,
        }
        for k, v in session.input_filters.items():
            if k in merged and v not in (None, ""):
                merged[k] = v

        params = build_ctgov_params(**merged)
        if not params:
            return "검색 필터가 비어 있습니다. 최소 하나의 조건(drug_name/condition/sponsor 등)을 지정하세요."

        studies, capped = client.search_studies(params, max_studies=settings.max_studies)
        session.searches[label] = SearchResult(
            label=label, studies=studies, capped=capped, filters={k: v for k, v in merged.items() if v}
        )
        session.index_studies(studies)
        if capped:
            session.notes.append(
                f"'{label}' 검색이 상한(MAX_STUDIES={settings.max_studies})에 걸려 상위 일부만 집계합니다."
            )
        return (
            f"label='{label}' 검색 완료: {len(studies)}건"
            f"{' (cap 도달, 표본 기준)' if capped else ''}. "
            f"적용 필터: {session.searches[label].filters}"
        )

    def _preview_rows(data: list[dict], key_fields: list[str], n: int = 8) -> str:
        rows = []
        for row in data[:n]:
            rows.append(", ".join(f"{k}={row.get(k)}" for k in key_fields))
        more = f" ... (+{len(data) - n} more)" if len(data) > n else ""
        return "; ".join(rows) + more

    @tool
    def aggregate_by(field: str, search_label: str = "default") -> str:
        """저장된 검색 결과를 특정 축으로 group-by 집계한다 (모든 수치는 서버가 계산).

        Args:
            field: 집계 축. 다음 중 하나 —
                'year'(연도별 추이), 'phase'(임상 단계 분포),
                'intervention_type'(중재 유형 분포), 'status'(모집 상태 분포),
                'country'(국가별 분포).
            search_label: 어떤 검색 결과를 집계할지. 기본 'default'.
        Returns:
            생성된 artifact_id와 상위 데이터 미리보기. 이 artifact_id를 finalize에 넘겨라.
        """
        if field not in FIELD_TO_KIND:
            return f"지원하지 않는 field '{field}'. 가능: {sorted(FIELD_TO_KIND)}"
        sr = session.searches.get(search_label)
        if sr is None:
            return f"search_label='{search_label}' 결과가 없습니다. 먼저 search_trials를 호출하세요."
        if not sr.studies:
            return f"'{search_label}' 검색 결과가 0건이라 집계할 수 없습니다."

        if field == "year":
            result = aggregate_time_trend(sr.studies)
            key_fields = ["year", "trial_count"]
        elif field == "country":
            result = aggregate_geo(sr.studies)
            key_fields = ["country", "trial_count"]
        else:
            result = aggregate_distribution(sr.studies, field)
            key_fields = ["category", "trial_count"]

        kind = FIELD_TO_KIND[field]
        aid = session.next_artifact_id(kind)
        session.artifacts[aid] = Artifact(
            artifact_id=aid,
            kind=kind,
            data=result["data"],
            buckets=result["buckets"],
            notes=result.get("notes", []),
            extra={"field": field},
        )
        return (
            f"artifact_id='{aid}' 생성 (kind={kind}, field={field}, "
            f"{len(result['data'])}개 그룹). 미리보기: {_preview_rows(result['data'], key_fields)}"
        )

    @tool
    def compare_groups(search_labels: list[str], field: str = "phase") -> str:
        """여러 검색 결과를 같은 축으로 나란히 비교 집계한다 (grouped bar chart용).

        먼저 각 대상을 서로 다른 label로 search_trials 해두고, 그 label들을 여기에 넘겨라.

        Args:
            search_labels: 비교할 검색 label 목록 (2개 이상).
            field: 비교 축. 'phase'(기본) 또는 'status'.
        Returns:
            생성된 artifact_id와 미리보기.
        """
        if len(search_labels) < 2:
            return "비교하려면 최소 2개의 search_label이 필요합니다."
        groups = []
        for lbl in search_labels:
            sr = session.searches.get(lbl)
            if sr is None:
                return f"search_label='{lbl}' 결과가 없습니다. 먼저 search_trials를 호출하세요."
            groups.append({"label": lbl, "studies": sr.studies})

        result = aggregate_comparison(groups, field=field)
        aid = session.next_artifact_id("comparison")
        session.artifacts[aid] = Artifact(
            artifact_id=aid,
            kind="comparison",
            data=result["data"],
            buckets=result["buckets"],
            notes=result.get("notes", []),
            extra={"group_labels": result["group_labels"], "field": field},
        )
        return (
            f"artifact_id='{aid}' 생성 (comparison, groups={result['group_labels']}, "
            f"{len(result['data'])}개 카테고리). 미리보기: {result['data'][:6]}"
        )

    @tool
    def build_network(dimension: str = "sponsor_drug", search_label: str = "default") -> str:
        """저장된 검색 결과로 엔티티 관계망을 만든다.

        Args:
            dimension: 'sponsor_drug'(스폰서↔약물) 또는 'drug_drug'(병용연구 약물↔약물 공동출현).
            search_label: 어떤 검색 결과를 쓸지. 기본 'default'.
        Returns:
            생성된 artifact_id와 상위 엣지 미리보기.
        """
        if dimension not in ("sponsor_drug", "drug_drug"):
            return "dimension은 'sponsor_drug' 또는 'drug_drug'만 가능합니다."
        sr = session.searches.get(search_label)
        if sr is None:
            return f"search_label='{search_label}' 결과가 없습니다. 먼저 search_trials를 호출하세요."
        if not sr.studies:
            return f"'{search_label}' 검색 결과가 0건이라 네트워크를 만들 수 없습니다."

        result = aggregate_network(sr.studies, dimension)
        aid = session.next_artifact_id("network")
        session.artifacts[aid] = Artifact(
            artifact_id=aid,
            kind="network",
            data=result["data"],
            buckets=result["buckets"],
            notes=result.get("notes", []),
            extra={"dimension": dimension},
        )
        top_edges = result["data"]["edges"][:5]
        return (
            f"artifact_id='{aid}' 생성 (network={dimension}, "
            f"노드 {len(result['data']['nodes'])}개, 엣지 {len(result['data']['edges'])}개). "
            f"상위 엣지: {top_edges}"
        )

    @tool
    def finalize_visualization(artifact_id: str, chart_type: str, title: str) -> str:
        """최종 시각화를 확정한다. 반드시 마지막에 한 번 호출하라.

        Args:
            artifact_id: 앞선 집계/네트워크 도구가 반환한 artifact_id.
            chart_type: time_series | bar_chart | grouped_bar_chart | network_graph 중 하나.
            title: 사람이 읽을 수 있는 차트 제목.
        Returns:
            확정 결과 메시지.
        """
        if chart_type not in ALLOWED_CHART_TYPES:
            return f"허용되지 않은 chart_type '{chart_type}'. 가능: {sorted(ALLOWED_CHART_TYPES)}"
        if artifact_id not in session.artifacts:
            return f"artifact_id='{artifact_id}'를 찾을 수 없습니다. 존재하는: {list(session.artifacts)}"
        artifact = session.artifacts[artifact_id]
        allowed = KIND_TO_CHART.get(artifact.kind, set())
        if chart_type not in allowed:
            return (
                f"artifact kind='{artifact.kind}'에는 chart_type={sorted(allowed)}만 가능합니다. "
                f"'{chart_type}'은(는) 이 kind와 맞지 않으니 규칙에 맞는 chart_type으로 다시 호출하세요."
            )
        session.final_artifact_id = artifact_id
        session.final_chart_type = chart_type
        session.final_title = title
        return f"확정 완료: {artifact_id} → {chart_type} ('{title}')"

    @tool
    def report_unresolvable(reason: str, missing: list[str] | None = None) -> str:
        """질문만으로 무엇을 조회할지 특정할 수 없을 때 호출한다 (honest abstention).

        조회 대상(질환/약물/스폰서/국가 등)이 질문에 전혀 없거나 너무 모호해서 근거 있는 검색을
        구성할 수 없을 때 사용하라. 절대 임의로 값을 지어내 검색하지 말고, 이 도구로 "특정 불가"를
        선언한 뒤 종료하라. 서버가 이를 사용자에게 그대로 전달한다.

        Args:
            reason: 왜 특정할 수 없는지 한 문장 설명.
            missing: 부족한 항목들 (예: ['condition', 'drug_name']).
        Returns:
            선언이 접수되었다는 메시지.
        """
        session.unresolved = {"reason": reason, "missing": missing or []}
        return f"특정 불가로 접수됨: {reason}. 추가 도구 호출 없이 종료하라."

    return [
        search_trials,
        aggregate_by,
        compare_groups,
        build_network,
        finalize_visualization,
        report_unresolvable,
    ]
