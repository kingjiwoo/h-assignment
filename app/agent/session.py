"""Shared state that all tools within a single request write to.

The agent (LLM) orchestrates, but every actual number/data point is computed and
stored on this Session by the tools. The final response is assembled by the server
straight out of Session artifacts — not from LLM text — so numbers cannot be
distorted by round-tripping through the LLM.
"""

from dataclasses import dataclass, field

from app.core import extractors as ex


@dataclass
class SearchResult:
    label: str
    studies: list[dict]
    capped: bool
    filters: dict


@dataclass
class Artifact:
    """A single aggregation result. Exactly one of these becomes the final visualization."""

    artifact_id: str
    kind: str  # time_trend | distribution | comparison | geo | network
    data: object  # list[dict] or {"nodes":..., "edges":...}
    buckets: dict  # bucket_key -> [nct_id]
    notes: list
    extra: dict = field(default_factory=dict)  # e.g., group_labels


@dataclass
class Session:
    input_filters: dict = field(default_factory=dict)  # Filters declared on the request (always win)
    searches: dict = field(default_factory=dict)  # label -> SearchResult
    artifacts: dict = field(default_factory=dict)  # artifact_id -> Artifact
    studies_by_nct: dict = field(default_factory=dict)  # Global index for citation lookup
    notes: list = field(default_factory=list)
    final_artifact_id: str | None = None
    final_chart_type: str | None = None
    final_title: str | None = None
    # Populated when the agent self-declares "cannot resolve what to query" (honest abstention, layer 1).
    # Shape: {"reason": str, "missing": [str, ...]}.
    unresolved: dict | None = None
    _artifact_seq: int = 0

    def index_studies(self, studies: list[dict]) -> None:
        for s in studies:
            self.studies_by_nct[ex.nct_id(s)] = s

    def next_artifact_id(self, kind: str) -> str:
        self._artifact_seq += 1
        return f"{kind}_{self._artifact_seq}"
