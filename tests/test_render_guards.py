"""Unit tests for the graph-output validation layers — offline, no LLM/network.

- B (kind↔chart_type consistency): the unified tools derive chart_type from kind
  deterministically, so the LLM path can never diverge. Only the safety-belt test
  against direct session tampering is kept.
- C (assemble_response downgrades empty data → no_data)
- H (aggregate honesty notes about sample size)
"""

import json
from pathlib import Path

from app.agent.runner import assemble_response
from app.agent.session import Artifact, SearchResult, Session
from app.agent.tools import make_tools
from app.core.aggregate import (
    aggregate_comparison,
    aggregate_distribution,
    aggregate_time_trend,
)

FIXTURE = json.loads((Path(__file__).parent / "fixtures" / "sample_studies.json").read_text())


class FakeClient:
    def __init__(self, studies):
        self._studies = studies

    def search_studies(self, params, max_studies):
        return list(self._studies), False

    def close(self):
        pass


def _tools(session, studies=FIXTURE):
    return {t.name: t for t in make_tools(session, FakeClient(studies))}


# ============================================================================
# B — Unified tools decide chart_type from kind automatically (no LLM path to override)
# ============================================================================


def test_B_analyze_network_locks_chart_to_network_graph():
    """analyze_network always commits kind=network with chart_type=network_graph."""
    s = Session(input_filters={})
    t = _tools(s)
    t["analyze_network"].invoke(
        {"dimension": "sponsor_drug", "title": "n", "condition": "diabetes"}
    )
    assert s.final_chart_type == "network_graph"
    assert s.artifacts[s.final_artifact_id].kind == "network"


def test_B_analyze_distribution_locks_chart_to_bar_chart():
    s = Session(input_filters={})
    t = _tools(s)
    t["analyze_distribution"].invoke(
        {"field": "phase", "title": "d", "condition": "diabetes"}
    )
    assert s.final_chart_type == "bar_chart"
    assert s.artifacts[s.final_artifact_id].kind == "distribution"


def test_B_analyze_time_trend_locks_chart_to_time_series():
    s = Session(input_filters={})
    t = _tools(s)
    t["analyze_time_trend"].invoke({"title": "y", "condition": "diabetes"})
    assert s.final_chart_type == "time_series"
    assert s.artifacts[s.final_artifact_id].kind == "time_trend"


# ============================================================================
# C — assemble_response downgrades empty data → no_data (assembly stage)
# ============================================================================


def test_C_empty_list_data_downgrades_to_no_data():
    """A finalized distribution artifact with data=[] gets downgraded to no_data."""
    s = Session(input_filters={"condition": "x"})
    s.searches["default"] = SearchResult(label="default", studies=[{"_": 1}], capped=False, filters={})
    s.artifacts["distribution_1"] = Artifact(
        artifact_id="distribution_1",
        kind="distribution",
        data=[],  # effectively empty
        buckets={},
        notes=[],
        extra={},
    )
    s.final_artifact_id = "distribution_1"
    s.final_chart_type = "bar_chart"
    s.final_title = "empty"

    resp = assemble_response(s)

    assert resp["visualization"]["type"] == "no_data"
    assert any("empty" in n for n in resp["meta"]["notes"])


def test_C_empty_network_data_downgrades_to_no_data():
    """Network artifact with empty nodes and edges is downgraded to no_data."""
    s = Session(input_filters={})
    s.searches["default"] = SearchResult(label="default", studies=[{"_": 1}], capped=False, filters={})
    s.artifacts["network_1"] = Artifact(
        artifact_id="network_1",
        kind="network",
        data={"nodes": [], "edges": []},
        buckets={},
        notes=[],
        extra={},
    )
    s.final_artifact_id = "network_1"
    s.final_chart_type = "network_graph"
    s.final_title = "empty net"

    resp = assemble_response(s)

    assert resp["visualization"]["type"] == "no_data"


# ============================================================================
# Safety belt — assemble_response re-checks kind↔chart_type (defends against session tampering)
# ============================================================================


def test_safety_belt_downgrades_kind_chart_mismatch():
    """Even if the session is forced to hold network + bar_chart, the final response is no_data."""
    s = Session(input_filters={})
    s.searches["default"] = SearchResult(label="default", studies=[{"_": 1}], capped=False, filters={})
    s.artifacts["network_1"] = Artifact(
        artifact_id="network_1",
        kind="network",
        data={"nodes": [{"id": "A"}], "edges": [{"source": "A", "target": "B", "weight": 1}]},
        buckets={},
        notes=[],
        extra={},
    )
    # On the normal path a tool auto-derives chart_type; here we simulate a bypass.
    s.final_artifact_id = "network_1"
    s.final_chart_type = "bar_chart"
    s.final_title = "should be downgraded"

    resp = assemble_response(s)

    assert resp["visualization"]["type"] == "no_data"
    assert any("consistency" in n for n in resp["meta"]["notes"])


# ============================================================================
# H — aggregation honesty notes about sample size
# ============================================================================


def test_H_time_trend_notes_include_sample_size():
    result = aggregate_time_trend(FIXTURE)
    assert result["notes"], "notes should be populated"
    assert f"{len(FIXTURE)} studies" in result["notes"][0]
    # The number of studies with a parseable StartDate is also disclosed.
    assert "parseable StartDate" in result["notes"][0]


def test_H_distribution_notes_include_sample_size():
    result = aggregate_distribution(FIXTURE, "phase")
    assert result["notes"]
    assert f"{len(FIXTURE)} studies" in result["notes"][0]
    assert "field=phase" in result["notes"][0]


def test_H_comparison_notes_show_per_group_totals():
    groups = [
        {"label": "A", "studies": FIXTURE[:2]},
        {"label": "B", "studies": FIXTURE[2:]},
    ]
    result = aggregate_comparison(groups, "phase")
    note = result["notes"][0]
    assert "A: 2 studies" in note
    assert "B: 1 studies" in note
    assert "field=phase" in note
