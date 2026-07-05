"""에이전트 도구 + 응답 조립의 오프라인 통합 테스트.

실제 LLM/네트워크 없이, 도구를 직접 순서대로 호출(에이전트가 할 오케스트레이션을 재현)하고
fixture 검색 결과를 주입해 조립 결과를 검증한다. CtGovClient는 fixture로 대체한다.
"""

import json
from pathlib import Path

from app.agent.runner import assemble_response
from app.agent.session import Session
from app.agent.tools import make_tools

FIXTURE = json.loads((Path(__file__).parent / "fixtures" / "sample_studies.json").read_text())


class FakeClient:
    """search_studies가 항상 fixture를 반환하는 가짜 클라이언트."""

    def __init__(self, studies):
        self._studies = studies

    def search_studies(self, params, max_studies):
        return list(self._studies), False

    def close(self):
        pass


def _tools(session, studies=FIXTURE):
    return {t.name: t for t in make_tools(session, FakeClient(studies))}


def test_distribution_flow_builds_bar_chart_with_citations():
    s = Session(input_filters={"condition": "diabetes"})
    t = _tools(s)
    t["search_trials"].invoke({"condition": "diabetes"})
    out = t["aggregate_by"].invoke({"field": "phase"})
    assert "artifact_id='distribution_1'" in out
    t["finalize_visualization"].invoke(
        {"artifact_id": "distribution_1", "chart_type": "bar_chart", "title": "Diabetes by phase"}
    )
    resp = assemble_response(s)

    assert resp["visualization"]["type"] == "bar_chart"
    counts = {r["category"]: r["trial_count"] for r in resp["visualization"]["data"]}
    assert counts == {"PHASE2": 1, "PHASE3": 1, "NA": 1}
    # citation: 각 버킷에 실제 nct_id + 발췌
    assert resp["citations"]["PHASE3"][0]["nct_id"] == "NCT001"
    assert resp["meta"]["analysis_type"] == "distribution"


def test_network_flow_builds_graph():
    s = Session(input_filters={})
    t = _tools(s)
    t["search_trials"].invoke({"condition": "diabetes"})
    t["build_network"].invoke({"dimension": "sponsor_drug"})
    t["finalize_visualization"].invoke(
        {"artifact_id": "network_1", "chart_type": "network_graph", "title": "net"}
    )
    resp = assemble_response(s)
    assert resp["visualization"]["type"] == "network_graph"
    assert resp["visualization"]["data"]["nodes"]
    assert resp["visualization"]["data"]["edges"]


def test_explicit_input_filter_overrides_llm_arg():
    # 요청에 condition=diabetes가 명시되면, LLM이 다른 condition을 줘도 무시되고 diabetes가 적용
    s = Session(input_filters={"condition": "diabetes"})
    t = _tools(s)
    t["search_trials"].invoke({"condition": "cancer"})  # LLM이 엉뚱하게 준 값
    assert s.searches["default"].filters["condition"] == "diabetes"


def test_no_finalize_returns_no_data():
    s = Session(input_filters={})
    t = _tools(s)
    t["search_trials"].invoke({"condition": "diabetes"})
    resp = assemble_response(s)  # finalize 안 함
    assert resp["visualization"]["type"] == "no_data"


def test_aggregate_without_search_is_guarded():
    s = Session(input_filters={})
    t = _tools(s)
    out = t["aggregate_by"].invoke({"field": "phase", "search_label": "missing"})
    assert "결과가 없습니다" in out
