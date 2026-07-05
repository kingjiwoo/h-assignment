"""Filter values → ClinicalTrials.gov API query params conversion (pure functions)."""


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
    """Build the CT.gov query-params dict from individual filter values.

    - Text search (query.*): CT.gov's search engine (Essie) already handles brand names,
      synonyms, and typos itself.
    - Phase and year range are ANDed together in filter.advanced using AREA clauses.
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
