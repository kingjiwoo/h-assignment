"""Unit tests for honest abstention (needs_clarification) — offline, no LLM/network.

Layer 1 (agent self-declaration) and layer 2 (deterministic backstop) each produce
needs_clarification, and both must remain cleanly distinguishable from the normal
and zero-result paths.
"""

from app.agent.runner import assemble_response
from app.agent.session import Artifact, SearchResult, Session


def test_layer1_report_unresolvable_yields_needs_clarification():
    """Layer 1: when the agent declares unresolved, the response is needs_clarification."""
    session = Session(input_filters={})
    session.unresolved = {"reason": "No condition or drug provided", "missing": ["condition", "drug_name"]}

    resp = assemble_response(session)

    assert resp["visualization"]["type"] == "needs_clarification"
    assert resp["clarification"]["reason"] == "No condition or drug provided"
    assert resp["clarification"]["missing"] == ["condition", "drug_name"]
    assert resp["clarification"]["suggestions"]  # Guidance messages are populated


def test_layer2_backstop_no_search_yields_needs_clarification():
    """Layer 2: even without an unresolved declaration, zero valid searches → needs_clarification."""
    session = Session(input_filters={})
    # No search, no finalize (the agent broke the rules and did nothing).

    resp = assemble_response(session)

    assert resp["visualization"]["type"] == "needs_clarification"
    assert resp["clarification"] is not None


def test_searched_but_zero_results_is_no_data_not_clarification():
    """Searched but 0 hits → no_data (not needs_clarification). Keep the two paths distinct."""
    session = Session(input_filters={"drug_name": "Zzzznonexistent"})
    session.searches["default"] = SearchResult(
        label="default", studies=[], capped=False, filters={"drug_name": "Zzzznonexistent"}
    )

    resp = assemble_response(session)

    assert resp["visualization"]["type"] == "no_data"
    assert resp.get("clarification") is None


def test_normal_finalized_visualization_is_unaffected():
    """A normal path (search + aggregate + finalize) yields a visualization untouched by clarification."""
    session = Session(input_filters={"condition": "diabetes"})
    session.searches["default"] = SearchResult(
        label="default", studies=[{"x": 1}], capped=False, filters={"condition": "diabetes"}
    )
    session.artifacts["distribution_1"] = Artifact(
        artifact_id="distribution_1",
        kind="distribution",
        data=[{"category": "PHASE3", "trial_count": 1}],
        buckets={"PHASE3": []},
        notes=[],
        extra={"field": "phase"},
    )
    session.final_artifact_id = "distribution_1"
    session.final_chart_type = "bar_chart"
    session.final_title = "Diabetes trials by phase"

    resp = assemble_response(session)

    assert resp["visualization"]["type"] == "bar_chart"
    assert resp.get("clarification") is None
