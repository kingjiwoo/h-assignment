"""LangGraph 상태 및 LLM이 채우는 Intent 모델."""

from typing import Literal, TypedDict

from pydantic import BaseModel, Field

from app.schemas import AnalysisType


class ComparisonGroup(BaseModel):
    """comparison 분석에서 비교 대상 한 그룹을 나타낸다. 예: {"label": "Drug A", "drug_name": "Aspirin"}."""

    label: str
    drug_name: str | None = None
    condition: str | None = None
    sponsor: str | None = None


class Intent(BaseModel):
    """자연어 query에서 LLM이 추출하는 구조화된 검색/분석 의도.

    LLM은 오직 '해석'만 담당한다. 실제 trial 수 같은 수치는 절대 생성하지 않으며,
    이후 결정론적 코드가 API 결과로부터 집계한다.
    """

    drug_name: str | None = Field(None, description="중재/약물명")
    condition: str | None = Field(None, description="질환명")
    sponsor: str | None = Field(None, description="스폰서명")
    country: str | None = Field(None, description="국가명")
    trial_phase: str | None = Field(
        None, description="phase 필터. PHASE1/PHASE2/PHASE3/PHASE4/EARLY_PHASE1/NA 중 하나"
    )
    start_year: int | None = Field(None, description="시작 연도 필터")
    end_year: int | None = Field(None, description="종료 연도 필터")
    overall_status: str | None = Field(
        None, description="모집 상태 필터. 예: RECRUITING, COMPLETED. 명시 없으면 null"
    )
    analysis_type: AnalysisType = Field(
        ...,
        description=(
            "질문이 요구하는 분석 유형. "
            "time_trend=연도별 추이, distribution=phase/intervention 분포, "
            "comparison=둘 이상 대상 비교, geo=국가별 분포, network=엔티티 관계망"
        ),
    )
    distribution_field: Literal["phase", "intervention_type", "status"] | None = Field(
        None, description="distribution일 때 무엇으로 나눌지. 기본 phase"
    )
    comparison_groups: list[ComparisonGroup] | None = Field(
        None, description="comparison일 때 비교할 그룹들 (2개 이상)"
    )
    network_dimension: Literal["sponsor_drug", "drug_drug"] | None = Field(
        None, description="network일 때 엣지 종류. sponsor_drug 또는 drug_drug"
    )
    notes: str | None = Field(None, description="해석 과정에서의 가정이나 주의점")


class GraphState(TypedDict, total=False):
    # 입력
    query: str
    input_filters: dict  # 요청에서 명시적으로 넘어온 구조화 필드 (LLM 값보다 우선)

    # 파이프라인 산출물
    intent: Intent
    ctgov_params: dict
    studies: list[dict]
    capped: bool
    aggregated: dict  # {"data": ..., "citations": {bucket_key: [ {nct_id, excerpt} ]}}

    # 출력
    chart_type: str
    visualization: dict
    meta: dict
    citations: dict | None
    error: str | None
