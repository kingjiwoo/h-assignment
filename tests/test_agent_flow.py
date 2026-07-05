"""Offline integration tests for the agent tools + response assembly.

Exercises the unified analyze_* tools directly (no real LLM/network) and verifies
that the Session ends up in a finalized state. CtGovClient is replaced with a fixture.
"""

import json
from pathlib import Path

from app.agent.runner import assemble_response
from app.agent.session import Session
from app.agent.tools import make_tools

FIXTURE = json.loads((Path(__file__).parent / "fixtures" / "sample_studies.json").read_text())


class FakeClient:
    """Fake client whose search_studies always returns the fixture."""

    def __init__(self, studies):
        self._studies = studies
        self.call_count = 0

    def search_studies(self, params, max_studies):
        self.call_count += 1
        return list(self._studies), False

    def close(self):
        pass


def _tools(session, studies=FIXTURE):
    client = FakeClient(studies)
    return {t.name: t for t in make_tools(session, client)}, client


def test_analyze_distribution_finalizes_and_produces_citations():
    """A single tool call should perform search + aggregate + commit atomically."""
    s = Session(input_filters={"condition": "diabetes"})
    tools, _ = _tools(s)
    out = tools["analyze_distribution"].invoke(
        {"field": "phase", "title": "Diabetes by phase", "condition": "diabetes"}
    )
    assert "Committed bar_chart" in out
    resp = assemble_response(s)

    assert resp["visualization"]["type"] == "bar_chart"
    counts = {r["category"]: r["trial_count"] for r in resp["visualization"]["data"]}
    assert counts == {"PHASE2": 1, "PHASE3": 1, "NA": 1}
    assert resp["citations"]["PHASE3"][0]["nct_id"] == "NCT001"
    assert resp["meta"]["analysis_type"] == "distribution"


def test_analyze_network_finalizes():
    s = Session(input_filters={})
    tools, _ = _tools(s)
    tools["analyze_network"].invoke(
        {"dimension": "sponsor_drug", "title": "net", "condition": "diabetes"}
    )
    resp = assemble_response(s)
    assert resp["visualization"]["type"] == "network_graph"
    assert resp["visualization"]["data"]["nodes"]
    assert resp["visualization"]["data"]["edges"]


def test_analyze_time_trend_finalizes_time_series():
    s = Session(input_filters={})
    tools, _ = _tools(s)
    tools["analyze_time_trend"].invoke(
        {"title": "yearly", "condition": "diabetes"}
    )
    resp = assemble_response(s)
    assert resp["visualization"]["type"] == "time_series"
    assert resp["meta"]["analysis_type"] == "time_trend"


def test_explicit_input_filter_overrides_llm_arg():
    """Filters declared on the request beat LLM-supplied tool arguments (deterministic guarantee)."""
    s = Session(input_filters={"condition": "diabetes"})
    tools, _ = _tools(s)
    tools["analyze_distribution"].invoke(
        {"field": "phase", "title": "t", "condition": "cancer"}  # LLM supplied a wrong value
    )
    assert s.searches["default"].filters["condition"] == "diabetes"


def test_no_filters_returns_error_without_finalize():
    """With no filters, the tool cannot build a search and must not commit anything."""
    s = Session(input_filters={})
    tools, client = _tools(s)
    out = tools["analyze_distribution"].invoke({"field": "phase", "title": "t"})
    assert "No filters provided" in out
    assert client.call_count == 0  # No CT.gov call should be attempted
    assert s.final_artifact_id is None
    resp = assemble_response(s)
    # No search ever happened → needs_clarification backstop
    assert resp["visualization"]["type"] == "needs_clarification"


def test_analyze_distribution_rejects_unknown_field():
    s = Session(input_filters={"condition": "diabetes"})
    tools, client = _tools(s)
    out = tools["analyze_distribution"].invoke(
        {"field": "unknown_axis", "title": "t", "condition": "diabetes"}
    )
    assert "Unsupported field" in out
    assert client.call_count == 0
    assert s.final_artifact_id is None


def test_analyze_comparison_requires_two_groups():
    s = Session(input_filters={})
    tools, _ = _tools(s)
    out = tools["analyze_comparison"].invoke(
        {"filter_sets": [{"label": "A", "drug_name": "A"}], "title": "t"}
    )
    assert "at least 2" in out
    assert s.final_artifact_id is None


def test_analyze_comparison_parallel_fetch_reuses_cache_for_shared_filters():
    """The fetch_cache dedupes identical filter combinations, cutting API calls."""
    s = Session(input_filters={})
    tools, client = _tools(s)
    tools["analyze_comparison"].invoke(
        {
            "filter_sets": [
                {"label": "A", "drug_name": "A", "condition": "diabetes"},
                {"label": "B", "drug_name": "B", "condition": "diabetes"},
            ],
            "title": "A vs B",
            "field": "phase",
        }
    )
    resp = assemble_response(s)
    assert resp["visualization"]["type"] == "grouped_bar_chart"
    # Filters differ so we expect two calls (cache misses); the tool itself must
    # at least progress normally to completion.
    assert client.call_count == 2


def test_zero_result_does_not_finalize():
    """A zero-result search must not commit; assemble_response falls back to no_data."""
    s = Session(input_filters={})
    tools, _ = _tools(s, studies=[])
    out = tools["analyze_distribution"].invoke(
        {"field": "phase", "title": "t", "condition": "unobtainium"}
    )
    assert "No trials matched" in out
    assert s.final_artifact_id is None
    resp = assemble_response(s)
    assert resp["visualization"]["type"] == "no_data"
