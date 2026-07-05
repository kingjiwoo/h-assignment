"""그래프 출력 검증 계층 단위 테스트 — LLM/네트워크 없이 오프라인 검증.

- B (kind↔chart_type 정합): 통합 도구가 kind에서 chart_type을 결정론적으로 확정하므로
  LLM 경로로는 어긋날 수 없다. 세션 직접 조작에 대한 안전벨트 테스트만 유지.
- C (assemble_response의 빈 data → no_data 강등)
- H (aggregate 표본 크기 정직성 노트)
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
# B — 통합 도구는 kind에서 chart_type을 자동 결정한다 (LLM이 뒤바꿀 통로 없음)
# ============================================================================


def test_B_analyze_network_locks_chart_to_network_graph():
    """analyze_network는 항상 kind=network, chart_type=network_graph를 확정한다."""
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
# C — assemble_response의 빈 data → no_data 강등 (조립 단계)
# ============================================================================


def test_C_empty_list_data_downgrades_to_no_data():
    """distribution artifact가 finalize됐지만 data가 [] → no_data로 강등."""
    s = Session(input_filters={"condition": "x"})
    s.searches["default"] = SearchResult(label="default", studies=[{"_": 1}], capped=False, filters={})
    s.artifacts["distribution_1"] = Artifact(
        artifact_id="distribution_1",
        kind="distribution",
        data=[],  # 실질 공허
        buckets={},
        notes=[],
        extra={},
    )
    s.final_artifact_id = "distribution_1"
    s.final_chart_type = "bar_chart"
    s.final_title = "empty"

    resp = assemble_response(s)

    assert resp["visualization"]["type"] == "no_data"
    assert any("비어" in n for n in resp["meta"]["notes"])


def test_C_empty_network_data_downgrades_to_no_data():
    """network artifact의 nodes/edges가 둘 다 비면 no_data 강등."""
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
# 안전벨트 — assemble_response의 kind↔chart_type 재검사 (세션 조작 우회 방어)
# ============================================================================


def test_safety_belt_downgrades_kind_chart_mismatch():
    """세션에 network artifact + bar_chart가 강제로 남아있어도 최종 응답에서 no_data 강등."""
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
    # 정상 경로에선 도구가 chart_type을 자동 결정하지만, 우회를 시뮬레이션.
    s.final_artifact_id = "network_1"
    s.final_chart_type = "bar_chart"
    s.final_title = "should be downgraded"

    resp = assemble_response(s)

    assert resp["visualization"]["type"] == "no_data"
    assert any("정합성" in n for n in resp["meta"]["notes"])


# ============================================================================
# H — aggregate 표본 크기 정직성 노트
# ============================================================================


def test_H_time_trend_notes_include_sample_size():
    result = aggregate_time_trend(FIXTURE)
    assert result["notes"], "notes가 채워져 있어야 한다"
    assert f"{len(FIXTURE)}건" in result["notes"][0]
    # StartDate 파싱된 건수도 함께 노출
    assert "파싱 가능한" in result["notes"][0]


def test_H_distribution_notes_include_sample_size():
    result = aggregate_distribution(FIXTURE, "phase")
    assert result["notes"]
    assert f"{len(FIXTURE)}건" in result["notes"][0]
    assert "field=phase" in result["notes"][0]


def test_H_comparison_notes_show_per_group_totals():
    groups = [
        {"label": "A", "studies": FIXTURE[:2]},
        {"label": "B", "studies": FIXTURE[2:]},
    ]
    result = aggregate_comparison(groups, "phase")
    note = result["notes"][0]
    assert "A: 2건" in note
    assert "B: 1건" in note
    assert "field=phase" in note
