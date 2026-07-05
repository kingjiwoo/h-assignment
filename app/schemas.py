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
    """POST /query 요청 스키마.

    query만 필수이며, 나머지 필드는 명시적으로 주어지면 LLM이 자연어에서 추출한 값보다
    항상 우선 적용된다 (결정론적 병합 규칙, graph/nodes/query_builder.py 참고).
    """

    query: str = Field(..., min_length=1, description="자연어 임상시험 질문")
    drug_name: str | None = Field(None, description="중재/약물명 (예: Pembrolizumab)")
    condition: str | None = Field(None, description="질환/컨디션명 (예: Breast Cancer)")
    sponsor: str | None = Field(None, description="스폰서명")
    country: str | None = Field(None, description="국가명")
    trial_phase: str | None = Field(
        None, description="임상시험 phase (예: PHASE1, PHASE2, PHASE3, PHASE4, NA, EARLY_PHASE1)"
    )
    start_year: int | None = Field(None, description="검색 시작 연도 (inclusive)")
    end_year: int | None = Field(None, description="검색 종료 연도 (inclusive)")


class Citation(BaseModel):
    nct_id: str
    excerpt: str


class Clarification(BaseModel):
    """질문만으로 무엇을 조회할지 특정할 수 없을 때, 사용자에게 무엇이 부족한지 알려준다.

    no_data(조회는 했으나 결과 0건)와 달리, needs_clarification은 '조회 대상 자체를 못 정함'을
    의미한다. 에이전트가 근거 없이 추측하는 대신 정직하게 "모르겠다"를 반환하기 위한 필드.
    """

    reason: str
    missing: list[str] = Field(default_factory=list, description="특정하지 못한 항목 (예: condition, drug_name)")
    suggestions: list[str] = Field(default_factory=list, description="사용자가 추가하면 좋은 정보 안내")


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
