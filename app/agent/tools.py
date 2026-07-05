"""에이전트 도구 세트 (통합판).

한 도구 = 한 분석 kind = 한 chart_type. 각 도구가 내부에서 검색 → 집계 → 확정을 원자적으로
수행하고, Session에 완결된 Artifact와 최종 상태(final_*)를 남긴다.

LLM은 "어떤 분석을 할지"만 결정한다. chart_type을 직접 지정할 통로가 없어 kind↔chart_type
정합성 오류가 원천 차단되며, 모든 수치는 결정론적 코어(app/core)가 실제 데이터로 계산한다.
"""

from concurrent.futures import ThreadPoolExecutor

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

# 각 분석 kind가 확정하는 chart_type — 1:1 결정론 매핑.
# assemble_response의 안전벨트가 이 표를 재확인해 세션 조작 등의 우회 경로도 방어한다.
KIND_TO_CHART: dict[str, str] = {
    "time_trend": "time_series",
    "distribution": "bar_chart",
    "geo": "bar_chart",
    "comparison": "grouped_bar_chart",
    "network": "network_graph",
}

DISTRIBUTION_FIELDS = {"phase", "intervention_type", "status"}
COMPARISON_FIELDS = {"phase", "status"}
NETWORK_DIMENSIONS = {"sponsor_drug", "drug_drug"}


def _merged_filters(session_filters: dict, tool_args: dict) -> dict:
    """요청에 명시된 필터는 LLM 인자보다 항상 우선한다(결정론적 보증)."""
    merged = dict(tool_args)
    for k, v in session_filters.items():
        if k in merged and v not in (None, ""):
            merged[k] = v
    return merged


def make_tools(session: Session, client: CtGovClient | None = None) -> list:
    """Session에 바인딩된 도구 리스트를 만든다 (요청마다 새로 생성)."""
    client = client or CtGovClient()

    # 요청 내 필터 조합별 CT.gov 응답 캐시.
    # 같은 필터로 여러 분석(예: 비교 시 A/B가 공통 필터를 공유)이 돌아도 API 호출은 1회.
    fetch_cache: dict[frozenset, tuple[list, bool]] = {}

    def _fetch(filter_kwargs: dict) -> tuple[list, bool, dict, dict]:
        """필터로 검색(캐시 재사용)하여 (studies, capped, ctgov_params, effective_filters)를 반환."""
        merged = _merged_filters(session.input_filters, filter_kwargs)
        effective = {k: v for k, v in merged.items() if v not in (None, "")}
        params = build_ctgov_params(**merged)
        if not params:
            return [], False, {}, effective
        key = frozenset(effective.items())
        if key in fetch_cache:
            studies, capped = fetch_cache[key]
        else:
            studies, capped = client.search_studies(params, max_studies=settings.max_studies)
            fetch_cache[key] = (studies, capped)
        return studies, capped, params, effective

    def _record_search(label: str, studies: list, capped: bool, effective_filters: dict) -> None:
        session.searches[label] = SearchResult(
            label=label, studies=studies, capped=capped, filters=effective_filters
        )
        session.index_studies(studies)
        if capped:
            note = f"'{label}' 검색이 상한(MAX_STUDIES={settings.max_studies})에 걸려 상위 일부만 집계합니다."
            if note not in session.notes:
                session.notes.append(note)

    def _finalize(kind: str, result: dict, title: str, extra: dict | None = None) -> str:
        aid = session.next_artifact_id(kind)
        session.artifacts[aid] = Artifact(
            artifact_id=aid,
            kind=kind,
            data=result["data"],
            buckets=result["buckets"],
            notes=result.get("notes", []),
            extra=extra or {},
        )
        session.final_artifact_id = aid
        session.final_chart_type = KIND_TO_CHART[kind]
        session.final_title = title
        return aid

    _NO_FILTERS_MSG = (
        "필터가 비어 있어 CT.gov 검색을 구성할 수 없습니다. "
        "drug_name/condition/sponsor/country 중 하나 이상을 지정하거나, "
        "질문에서 그 정보를 특정할 수 없다면 report_unresolvable을 호출하세요."
    )

    @tool
    def analyze_time_trend(
        title: str,
        drug_name: str | None = None,
        condition: str | None = None,
        sponsor: str | None = None,
        country: str | None = None,
        trial_phase: str | None = None,
        start_year: int | None = None,
        end_year: int | None = None,
        overall_status: str | None = None,
    ) -> str:
        """연도별 시험 수 추이(time_series)를 계산·확정한다.

        Args:
            title: 사람이 읽을 수 있는 차트 제목.
            drug_name/condition/sponsor/country/trial_phase/start_year/end_year/overall_status:
                CT.gov 검색 필터. 최소 하나 이상 필요.
        Returns:
            확정 요약 (artifact_id, 데이터 포인트 수, 검색 규모).
        """
        filter_kwargs = {
            "drug_name": drug_name, "condition": condition, "sponsor": sponsor,
            "country": country, "trial_phase": trial_phase,
            "start_year": start_year, "end_year": end_year,
            "overall_status": overall_status,
        }
        studies, capped, params, effective = _fetch(filter_kwargs)
        if not params:
            return _NO_FILTERS_MSG
        _record_search("default", studies, capped, effective)
        if not studies:
            return f"조건에 맞는 시험이 0건입니다 (filters={effective}). 시각화를 확정하지 않습니다."
        result = aggregate_time_trend(studies)
        aid = _finalize("time_trend", result, title)
        return (
            f"time_series 확정: artifact_id='{aid}', 연도 {len(result['data'])}개, "
            f"검색 {len(studies)}건{' (cap 도달)' if capped else ''}."
        )

    @tool
    def analyze_distribution(
        field: str,
        title: str,
        drug_name: str | None = None,
        condition: str | None = None,
        sponsor: str | None = None,
        country: str | None = None,
        trial_phase: str | None = None,
        start_year: int | None = None,
        end_year: int | None = None,
        overall_status: str | None = None,
    ) -> str:
        """카테고리 분포(bar_chart)를 계산·확정한다.

        Args:
            field: 'phase' | 'intervention_type' | 'status' | 'country'.
                'country'는 국가별 시험 수 지리 분포로 처리된다.
            title: 차트 제목.
            (나머지 검색 필터는 analyze_time_trend와 동일)
        """
        if field != "country" and field not in DISTRIBUTION_FIELDS:
            return f"field='{field}' 미지원. 가능: {sorted(DISTRIBUTION_FIELDS | {'country'})}"
        filter_kwargs = {
            "drug_name": drug_name, "condition": condition, "sponsor": sponsor,
            "country": country, "trial_phase": trial_phase,
            "start_year": start_year, "end_year": end_year,
            "overall_status": overall_status,
        }
        studies, capped, params, effective = _fetch(filter_kwargs)
        if not params:
            return _NO_FILTERS_MSG
        _record_search("default", studies, capped, effective)
        if not studies:
            return f"조건에 맞는 시험이 0건입니다 (filters={effective})."
        if field == "country":
            result = aggregate_geo(studies)
            kind = "geo"
        else:
            result = aggregate_distribution(studies, field)
            kind = "distribution"
        aid = _finalize(kind, result, title, extra={"field": field})
        return (
            f"bar_chart 확정: artifact_id='{aid}', kind={kind}, "
            f"카테고리 {len(result['data'])}개, 검색 {len(studies)}건."
        )

    @tool
    def analyze_comparison(
        filter_sets: list[dict],
        title: str,
        field: str = "phase",
    ) -> str:
        """여러 대상을 같은 축(field)으로 나란히 비교(grouped_bar_chart)해 확정한다.

        Args:
            filter_sets: 각 대상의 필터. 최소 2개 원소, 각 원소는
                {"label": <표시명>, "drug_name": ..., "condition": ..., ...} 형태.
                label은 서로 달라야 하고, label 외 필터 중 하나 이상은 있어야 한다.
            title: 차트 제목.
            field: 비교 축. 'phase'(기본) 또는 'status'.
        """
        if len(filter_sets) < 2:
            return "비교하려면 최소 2개의 filter_sets가 필요합니다."
        if field not in COMPARISON_FIELDS:
            return f"field='{field}' 미지원. 가능: {sorted(COMPARISON_FIELDS)}"
        labels = [fs.get("label") for fs in filter_sets]
        if any(not lbl for lbl in labels):
            return "filter_sets의 각 원소에 'label'을 지정하세요."
        if len(set(labels)) != len(labels):
            return "filter_sets의 label은 서로 달라야 합니다."

        def _one(fs: dict):
            fk = {k: v for k, v in fs.items() if k != "label"}
            return fs["label"], _fetch(fk)

        # 병렬 fetch — 같은 필터는 fetch_cache가 자동 dedupe.
        with ThreadPoolExecutor(max_workers=min(len(filter_sets), 4)) as pool:
            fetched = list(pool.map(_one, filter_sets))

        groups = []
        for label, (studies, capped, params, effective) in fetched:
            if not params:
                return f"label='{label}'의 필터가 비어 있습니다. {_NO_FILTERS_MSG}"
            _record_search(label, studies, capped, effective)
            groups.append({"label": label, "studies": studies})

        if all(len(g["studies"]) == 0 for g in groups):
            return "모든 대상의 검색 결과가 0건이라 비교할 수 없습니다."

        result = aggregate_comparison(groups, field=field)
        aid = _finalize(
            "comparison",
            result,
            title,
            extra={"group_labels": result["group_labels"], "field": field},
        )
        return (
            f"grouped_bar_chart 확정: artifact_id='{aid}', "
            f"groups={result['group_labels']}, 카테고리 {len(result['data'])}개."
        )

    @tool
    def analyze_network(
        dimension: str,
        title: str,
        drug_name: str | None = None,
        condition: str | None = None,
        sponsor: str | None = None,
        country: str | None = None,
        trial_phase: str | None = None,
        start_year: int | None = None,
        end_year: int | None = None,
        overall_status: str | None = None,
    ) -> str:
        """엔티티 관계망(network_graph)을 계산·확정한다.

        Args:
            dimension: 'sponsor_drug'(스폰서↔약물) 또는 'drug_drug'(병용연구 약물↔약물 공동출현).
            title: 차트 제목.
            (검색 필터는 analyze_time_trend와 동일)
        """
        if dimension not in NETWORK_DIMENSIONS:
            return f"dimension='{dimension}' 미지원. 가능: {sorted(NETWORK_DIMENSIONS)}"
        filter_kwargs = {
            "drug_name": drug_name, "condition": condition, "sponsor": sponsor,
            "country": country, "trial_phase": trial_phase,
            "start_year": start_year, "end_year": end_year,
            "overall_status": overall_status,
        }
        studies, capped, params, effective = _fetch(filter_kwargs)
        if not params:
            return _NO_FILTERS_MSG
        _record_search("default", studies, capped, effective)
        if not studies:
            return f"조건에 맞는 시험이 0건입니다 (filters={effective})."
        result = aggregate_network(studies, dimension)
        aid = _finalize("network", result, title, extra={"dimension": dimension})
        return (
            f"network_graph 확정: artifact_id='{aid}', "
            f"노드 {len(result['data']['nodes'])}개, 엣지 {len(result['data']['edges'])}개."
        )

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
        analyze_time_trend,
        analyze_distribution,
        analyze_comparison,
        analyze_network,
        report_unresolvable,
    ]
