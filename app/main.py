"""FastAPI 진입점. POST /query 하나로 전체 파이프라인을 노출한다."""

import logging

from fastapi import FastAPI

from app.graph.build import compiled_graph
from app.schemas import QueryRequest, QueryResponse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ctgov-viz")

app = FastAPI(
    title="ClinicalTrials.gov Query-to-Visualization Agent",
    description="자연어 임상시험 질문을 구조화된 시각화 스펙(JSON)으로 변환하는 백엔드",
    version="0.1.0",
)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/query", response_model=QueryResponse)
def query(req: QueryRequest) -> QueryResponse:
    # 명시적으로 주어진 구조화 필드만 추려 LLM 값보다 우선하도록 전달
    input_filters = req.model_dump(exclude_none=True, exclude={"query"})

    result = compiled_graph.invoke(
        {"query": req.query, "input_filters": input_filters}
    )

    return QueryResponse(
        visualization=result["visualization"],
        meta=result["meta"],
        citations=result.get("citations"),
    )
