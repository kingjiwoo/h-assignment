"""필터 값 → ClinicalTrials.gov API query params 변환 (순수 함수)."""


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
    """개별 필터 값들로부터 CT.gov query params dict를 만든다.

    - 텍스트 검색(query.*)은 CT.gov 검색엔진(Essie)이 브랜드명/동의어/오타를 자체 처리한다.
    - phase와 연도 범위는 filter.advanced의 AREA 절로 AND 결합한다.
    """
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
