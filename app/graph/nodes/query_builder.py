"""query_builder 노드 — Intent + 명시적 입력 필터를 CT.gov API 파라미터로 변환한다.

전적으로 결정론적이다. 명시적으로 요청에 들어온 구조화 필드는 LLM이 추출한 값보다 항상 우선한다.
"""

from app.graph.state import GraphState, Intent

# comparison 그룹 하나를 CT.gov 파라미터로 만들 때도 재사용하기 위해 필터 병합을 함수로 분리.


def _merged_value(field: str, intent: Intent, input_filters: dict):
    """명시적 입력값 우선, 없으면 intent 값."""
    if input_filters.get(field) not in (None, ""):
        return input_filters[field]
    return getattr(intent, field, None)


def build_ctgov_params(
    *,
    drug_name: str | None = None,
    condition: str | None = None,
    sponsor: str | None = None,
    country: str | None = None,
    trial_phase: str | None = None,
    start_year: int | None = None,
    end_year: int | None = None,
    overall_status: str | None = None,
) -> dict:
    """개별 필터 값들로부터 CT.gov query params dict를 만든다 (comparison 그룹에도 재사용)."""
    params: dict = {}
    if drug_name:
        params["query.intr"] = drug_name
    if condition:
        params["query.cond"] = condition
    if sponsor:
        params["query.spons"] = sponsor
    if country:
        params["query.locn"] = country
    if overall_status:
        params["filter.overallStatus"] = overall_status

    advanced_clauses: list[str] = []
    if trial_phase:
        advanced_clauses.append(f"AREA[Phase]{trial_phase}")
    if start_year or end_year:
        lo = f"{start_year}-01-01" if start_year else "MIN"
        hi = f"{end_year}-12-31" if end_year else "MAX"
        advanced_clauses.append(f"AREA[StartDate]RANGE[{lo},{hi}]")
    if advanced_clauses:
        params["filter.advanced"] = " AND ".join(advanced_clauses)

    return params


def query_builder_node(state: GraphState) -> dict:
    intent: Intent = state["intent"]
    input_filters = state.get("input_filters", {})

    params = build_ctgov_params(
        drug_name=_merged_value("drug_name", intent, input_filters),
        condition=_merged_value("condition", intent, input_filters),
        sponsor=_merged_value("sponsor", intent, input_filters),
        country=_merged_value("country", intent, input_filters),
        trial_phase=_merged_value("trial_phase", intent, input_filters),
        start_year=_merged_value("start_year", intent, input_filters),
        end_year=_merged_value("end_year", intent, input_filters),
        overall_status=getattr(intent, "overall_status", None),
    )

    return {"ctgov_params": params}
