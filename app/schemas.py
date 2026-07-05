from typing import Literal

from pydantic import BaseModel, Field

ChartType = Literal[
    "bar_chart",
    "grouped_bar_chart",
    "time_series",
    "scatter_plot",
    "histogram",
    "network_graph",
    "no_data",
    "needs_clarification",
]

AnalysisType = Literal["time_trend", "distribution", "comparison", "geo", "network"]


class QueryRequest(BaseModel):
    """Request schema for POST /query.

    Only `query` is required; every other field, when supplied explicitly, always
    takes precedence over values the LLM might extract from the natural-language
    query (deterministic merge rule — see the tool layer).
    """

    query: str = Field(..., min_length=1, description="Natural-language clinical-trial question")
    drug_name: str | None = Field(None, description="Intervention/drug name (e.g., Pembrolizumab)")
    condition: str | None = Field(None, description="Condition (e.g., Breast Cancer)")
    sponsor: str | None = Field(None, description="Sponsor name")
    country: str | None = Field(None, description="Country name")
    trial_phase: str | None = Field(
        None, description="Trial phase (e.g., PHASE1, PHASE2, PHASE3, PHASE4, NA, EARLY_PHASE1)"
    )
    start_year: int | None = Field(None, description="Search start year (inclusive)")
    end_year: int | None = Field(None, description="Search end year (inclusive)")


class Citation(BaseModel):
    nct_id: str
    excerpt: str


class Clarification(BaseModel):
    """Tells the user what is missing when the question alone cannot pin down the target.

    Unlike no_data (searched but returned 0 results), needs_clarification means "the
    target itself could not be determined." This field exists so the agent can honestly
    say "don't know" instead of guessing without grounding.
    """

    reason: str
    missing: list[str] = Field(default_factory=list, description="Items that could not be pinned down (e.g., condition, drug_name)")
    suggestions: list[str] = Field(default_factory=list, description="Guidance on what the user could add")


class VisualizationSpec(BaseModel):
    type: ChartType
    title: str
    encoding: dict = Field(default_factory=dict)
    data: list[dict] | dict = Field(default_factory=list)


class ResponseMeta(BaseModel):
    filters: dict = Field(default_factory=dict)
    analysis_type: AnalysisType | None = None
    source: str = "clinicaltrials.gov"
    study_count: int = 0
    capped: bool = False
    notes: list[str] = Field(default_factory=list)


class QueryResponse(BaseModel):
    visualization: VisualizationSpec
    meta: ResponseMeta
    citations: dict[str, list[Citation]] | None = None
    clarification: Clarification | None = None
