"""그래프 출력 검증 계층 단위 테스트 — LLM/네트워크 없이 오프라인 검증.

세 계층을 함께 확인한다:
- 안(tool): finalize_visualization의 kind↔chart_type 정합 검사 (B)
- 밖(assemble): 빈 data → no_data 강등 (C), 안전벨트 kind↔chart_type 재검사
- aggregate 표본 크기 정직성 노트 (H)
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
# B — finalize_visualization의 kind↔chart_type 정합 검사 (도구 내부)
# ============================================================================


def test_B_finalize_rejects_network_with_bar_chart():
    """network artifact를 bar_chart로 확정하려 하면 에러 문자열 반환, 세션 상태 미변경."""
    s = Session(input_filters={})
    t = _tools(s)
    t["search_trials"].invoke({"condition": "diabetes"})
    t["build_network"].invoke({"dimension": "sponsor_drug"})
    # 잘못된 조합 시도
    out = t["finalize_visualization"].invoke(
        {"artifact_id": "network_1", "chart_type": "bar_chart", "title": "wrong"}
    )
    assert "kind='network'" in out
    assert "network_graph" in out  # 어떤 것이 가능한지 안내
    # 세션은 아직 확정 안 됨 → LLM이 다시 시도할 여지
    assert s.final_artifact_id is None
    assert s.final_chart_type is None


def test_B_finalize_rejects_distribution_with_grouped_bar():
    """distribution artifact를 grouped_bar_chart로 확정 시도 → 거절."""
    s = Session(input_filters={})
    t = _tools(s)
    t["search_trials"].invoke({"condition": "diabetes"})
    t["aggregate_by"].invoke({"field": "phase"})
    out = t["finalize_visualization"].invoke(
        {"artifact_id": "distribution_1", "chart_type": "grouped_bar_chart", "title": "wrong"}
    )
    assert "kind='distribution'" in out
    assert s.final_artifact_id is None


def test_B_finalize_accepts_matching_pair():
    """올바른 kind↔chart_type 쌍은 정상 확정."""
    s = Session(input_filters={})
    t = _tools(s)
    t["search_trials"].invoke({"condition": "diabetes"})
    t["aggregate_by"].invoke({"field": "year"})
    out = t["finalize_visualization"].invoke(
        {"artifact_id": "time_trend_1", "chart_type": "time_series", "title": "yearly"}
    )
    assert "확정 완료" in out
    assert s.final_artifact_id == "time_trend_1"
    assert s.final_chart_type == "time_series"


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
# 안전벨트 — assemble_response의 kind↔chart_type 재검사 (조립 단계, B 백스톱)
# ============================================================================


def test_safety_belt_downgrades_kind_chart_mismatch():
    """B가 뚫려 network artifact + bar_chart가 세션에 남아있어도 최종 응답에서 no_data 강등."""
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
    # 정합 검사 우회 시나리오를 시뮬레이션 (직접 세션에 쓰는 극단 케이스)
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
