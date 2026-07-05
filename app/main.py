"""FastAPI entrypoint. Exposes the whole pipeline behind a single POST /query."""

import logging
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.agent.runner import run_agent
from app.schemas import QueryRequest, QueryResponse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ctgov-viz")

app = FastAPI(
    title="ClinicalTrials.gov Query-to-Visualization Agent",
    description="Backend that turns natural-language clinical-trial questions into structured visualization specs (JSON)",
    version="0.1.0",
)

_default_origins = "http://localhost:3000,http://127.0.0.1:3000"
_allowed_origins = [
    o.strip() for o in os.getenv("CORS_ALLOW_ORIGINS", _default_origins).split(",") if o.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/query", response_model=QueryResponse)
def query(req: QueryRequest) -> QueryResponse:
    # Only pass explicitly supplied structured fields, so they win over LLM-extracted values.
    input_filters = req.model_dump(exclude_none=True, exclude={"query"})

    result = run_agent(req.query, input_filters)

    return QueryResponse(
        visualization=result["visualization"],
        meta=result["meta"],
        citations=result.get("citations"),
        clarification=result.get("clarification"),
    )
