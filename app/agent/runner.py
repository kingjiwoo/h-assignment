"""Agent execution and final response assembly.

Flow: request → create_react_agent (tools = deterministic-core wrappers) orchestrates →
the server pulls the artifact the tool committed from the Session and assembles the
QueryResponse. Numbers never pass through LLM-generated text.
"""

from langgraph.prebuilt import create_react_agent

from app.agent.session import Artifact, Session
from app.agent.tools import KIND_TO_CHART, make_tools
from app.core import extractors as ex
from app.services.ctgov_client import CtGovClient
from app.services.llm import get_chat_model

MAX_CITATIONS_PER_BUCKET = 3

SYSTEM_PROMPT = """\
You are a data-analysis agent that answers clinical-trial questions with visualizations.

Pick exactly one tool and call it to commit an answer:
- analyze_time_trend    — yearly trial-count trend (time_series)
- analyze_distribution  — phase/intervention_type/status/country distribution (bar_chart)
- analyze_comparison    — side-by-side comparison of two or more targets (grouped_bar_chart)
- analyze_network       — sponsor↔drug or drug↔drug relationship graph (network_graph)
- report_unresolvable   — when the target cannot be pinned down (honest abstention)

Rules:
0) If the question does not name (or is too vague to identify) a target
   (condition/drug/sponsor/country, etc.), do NOT invent values. Call
   report_unresolvable(reason, missing) and stop. "Say you don't know" wins over guessing.
1) Each analyze_* tool performs search → aggregate → commit atomically inside.
   In principle call a tool only once per question; subsequent calls overwrite the result.
2) Never fabricate numbers yourself. Tools compute everything from real data.
3) If a search returns zero results or a filter-missing error, do not force another tool —
   just stop.
4) Use analyze_comparison(filter_sets=[{label, ...filters}, ...], field='phase'|'status')
   for comparisons. Do not fake it with multiple analyze_distribution calls.
"""

# Per-chart-type encoding — fixed so the frontend can render without guessing.
STATIC_ENCODINGS = {
    "time_series": {"x": {"field": "year", "type": "temporal"}, "y": {"field": "trial_count", "type": "quantitative"}},
    "network_graph": {"nodes": {"id": "id", "group": "kind", "size": "degree"}, "edges": {"source": "source", "target": "target", "weight": "weight"}},
}


def _encoding_for(chart_type: str, artifact: Artifact) -> dict:
    if chart_type == "grouped_bar_chart":
        return {
            "x": {"field": "category", "type": "nominal"},
            "y": {"field": "<group>", "type": "quantitative"},
            "series": artifact.extra.get("group_labels", []),
        }
    if chart_type == "bar_chart":
        data = artifact.data or []
        if data and "country" in data[0]:
            return {"x": {"field": "country", "type": "nominal"}, "y": {"field": "trial_count", "type": "quantitative"}}
        return {"x": {"field": "category", "type": "nominal"}, "y": {"field": "trial_count", "type": "quantitative"}}
    return STATIC_ENCODINGS.get(chart_type, {})


def _build_citations(artifact: Artifact, session: Session) -> dict | None:
    citations: dict = {}
    for bucket_key, ncts in artifact.buckets.items():
        refs = []
        for nct in ncts[:MAX_CITATIONS_PER_BUCKET]:
            study = session.studies_by_nct.get(nct)
            if study:
                refs.append({"nct_id": nct, "excerpt": ex.brief_title(study)})
        if refs:
            citations[bucket_key] = refs
    return citations or None


def _total_studies(session: Session) -> int:
    return sum(len(sr.studies) for sr in session.searches.values())


def _no_data_response(session: Session, reason: str) -> dict:
    return {
        "visualization": {"type": "no_data", "title": "No results", "encoding": {}, "data": []},
        "meta": {
            "filters": session.input_filters,
            "analysis_type": None,
            "source": "clinicaltrials.gov",
            "study_count": _total_studies(session),
            "capped": any(sr.capped for sr in session.searches.values()),
            "notes": session.notes + [reason],
        },
        "citations": None,
    }


# Per-missing-item guidance messages surfaced to the user.
_SUGGESTION_MAP = {
    "condition": "Please provide a condition (e.g., 'melanoma', 'diabetes').",
    "drug_name": "Please provide a drug/intervention name (e.g., 'Pembrolizumab').",
    "sponsor": "Please provide a sponsor name.",
    "country": "Please provide a country (e.g., 'Canada').",
}


def _needs_clarification_response(session: Session, reason: str, missing: list[str]) -> dict:
    """Response used when the target of the query cannot be pinned down (honest abstention).

    Distinct terminal state from no_data (searched but 0 hits). The clarification
    field tells the user what is missing and how to fix it.
    """
    suggestions = [_SUGGESTION_MAP[m] for m in missing if m in _SUGGESTION_MAP]
    if not suggestions:
        suggestions = ["Please include at least one of condition, drug, sponsor, or country in your question."]
    return {
        "visualization": {
            "type": "needs_clarification",
            "title": "Cannot pinpoint the question",
            "encoding": {},
            "data": [],
        },
        "meta": {
            "filters": session.input_filters,
            "analysis_type": None,
            "source": "clinicaltrials.gov",
            "study_count": 0,
            "capped": False,
            "notes": session.notes + [reason],
        },
        "citations": None,
        "clarification": {"reason": reason, "missing": missing, "suggestions": suggestions},
    }


def assemble_response(session: Session) -> dict:
    """Assemble the final QueryResponse dict from Session state (artifacts filled by tools).

    This is a pure assembly step independent of the LLM, so it is testable/reusable offline.
    """
    # Layer 1: the agent explicitly declared 'unresolvable' (honest abstention over guessing).
    if session.unresolved:
        return _needs_clarification_response(
            session,
            session.unresolved.get("reason") or "The question does not pin down what to query.",
            session.unresolved.get("missing") or [],
        )

    if not session.final_artifact_id:
        # Layer 2 (deterministic backstop): even if the LLM broke the rules and skipped
        # report_unresolvable, having zero valid searches means the target was never
        # identified → needs_clarification.
        if not session.searches:
            return _needs_clarification_response(
                session,
                "The question does not identify which clinical trials to look up.",
                ["condition", "drug_name", "sponsor"],
            )
        # Searched but zero hits → no_data (target was identified, data is missing).
        if _total_studies(session) == 0:
            return _no_data_response(session, "No trials matched the filters.")
        # Searches happened but no visualization was committed (agent didn't finish).
        return _no_data_response(session, "The agent did not commit a visualization.")

    artifact = session.artifacts[session.final_artifact_id]
    chart_type = session.final_chart_type

    # Safety belt: tools derive chart_type from kind, so on the happy path this can't
    # diverge. But session tampering / bypasses might, so we re-check at assembly time.
    # If it slips through, the encoding won't match the data keys and the frontend
    # cannot render.
    expected_chart = KIND_TO_CHART.get(artifact.kind)
    if expected_chart is None or chart_type != expected_chart:
        return _no_data_response(
            session,
            f"Internal consistency error: artifact.kind='{artifact.kind}' does not match chart_type='{chart_type}'.",
        )

    # If the aggregation result is effectively empty, downgrade to no_data instead of
    # rendering an empty chart (handles both list and dict shapes).
    data = artifact.data
    empty = (
        (isinstance(data, list) and not data)
        or (
            isinstance(data, dict)
            and not data.get("nodes")
            and not data.get("edges")
        )
    )
    if empty:
        return _no_data_response(session, "Aggregation result is empty.")

    notes = list(session.notes) + list(artifact.notes)

    return {
        "visualization": {
            "type": chart_type,
            "title": session.final_title or "Clinical trials",
            "encoding": _encoding_for(chart_type, artifact),
            "data": artifact.data,
        },
        "meta": {
            "filters": session.input_filters,
            "analysis_type": artifact.kind,
            "source": "clinicaltrials.gov",
            "study_count": _total_studies(session),
            "capped": any(sr.capped for sr in session.searches.values()),
            "notes": notes,
        },
        "citations": _build_citations(artifact, session),
    }


def run_agent(query: str, input_filters: dict) -> dict:
    """End-to-end run: the LLM agent orchestrates tools, then the server assembles the response."""
    session = Session(input_filters=input_filters or {})
    client = CtGovClient()
    try:
        agent = create_react_agent(get_chat_model(), make_tools(session, client))
        agent.invoke(
            {"messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": query},
            ]},
            config={"recursion_limit": 25},
        )
    finally:
        client.close()
    return assemble_response(session)
