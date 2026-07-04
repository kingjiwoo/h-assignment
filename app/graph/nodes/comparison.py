"""comparison 노드 — 각 비교 그룹을 개별 검색해 나란히 집계한다.

comparison은 "Drug A vs Drug B" 처럼 그룹마다 다른 필터로 별도 조회가 필요하므로
단일 fetch_node 경로를 쓰지 않고 이 노드가 그룹별 fetch + 집계를 직접 수행한다.
그룹에 지정되지 않은 필터(예: 공통 condition)는 intent의 값을 공유한다.
"""

from app.config import settings
from app.graph.nodes.aggregate import aggregate_comparison
from app.graph.nodes.query_builder import build_ctgov_params
from app.graph.state import GraphState
from app.services.ctgov_client import CtGovClient


def comparison_node(state: GraphState) -> dict:
    intent = state["intent"]
    input_filters = state.get("input_filters", {})
    groups = intent.comparison_groups or []

    # 그룹이 부실하면(1개 이하) 비교가 성립하지 않음 → 빈 결과로 두어 이후 no_data 처리.
    if len(groups) < 2:
        return {"studies": [], "capped": False, "aggregated": {"data": [], "buckets": {}}}

    # 모든 그룹이 공유하는 기본 필터 (그룹이 자체 값으로 덮어쓰지 않는 한 적용)
    shared = {
        "condition": input_filters.get("condition") or intent.condition,
        "sponsor": input_filters.get("sponsor") or intent.sponsor,
        "country": input_filters.get("country") or intent.country,
        "trial_phase": input_filters.get("trial_phase") or intent.trial_phase,
        "start_year": input_filters.get("start_year") or intent.start_year,
        "end_year": input_filters.get("end_year") or intent.end_year,
        "overall_status": intent.overall_status,
    }

    client = CtGovClient()
    total = 0
    any_capped = False
    agg_groups = []
    # 그룹이 많을수록 그룹당 상한을 낮춰 총량을 제어한다.
    per_group_cap = max(50, settings.max_studies // max(len(groups), 1))
    try:
        for g in groups:
            filters = {**shared}
            for key in ("drug_name", "condition", "sponsor"):
                if getattr(g, key, None):
                    filters[key] = getattr(g, key)
            params = build_ctgov_params(**filters)
            studies, capped = client.search_studies(params, max_studies=per_group_cap)
            any_capped = any_capped or capped
            total += len(studies)
            agg_groups.append({"label": g.label, "studies": studies})
    finally:
        client.close()

    result = aggregate_comparison(agg_groups, field="phase")
    return {
        "studies": [s for g in agg_groups for s in g["studies"]],
        "capped": any_capped,
        "aggregated": result,
    }
