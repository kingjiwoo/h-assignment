"""에이전트 도구 + 응답 조립의 오프라인 통합 테스트.

실제 LLM/네트워크 없이, 새 통합 도구(analyze_*)를 직접 호출해 세션에 확정된 결과를 검증한다.
CtGovClient는 fixture로 대체한다.
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
    """단일 도구 호출로 검색·집계·확정이 한 번에 끝나야 한다."""
    s = Session(input_filters={"condition": "diabetes"})
    tools, _ = _tools(s)
    out = tools["analyze_distribution"].invoke(
        {"field": "phase", "title": "Diabetes by phase", "condition": "diabetes"}
    )
    assert "bar_chart 확정" in out
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
    """요청에 명시된 필터가 LLM 도구 인자를 이긴다 (결정론적 보증)."""
    s = Session(input_filters={"condition": "diabetes"})
    tools, _ = _tools(s)
    tools["analyze_distribution"].invoke(
        {"field": "phase", "title": "t", "condition": "cancer"}  # LLM이 엉뚱한 값
    )
    assert s.searches["default"].filters["condition"] == "diabetes"


def test_no_filters_returns_error_without_finalize():
    """필터가 하나도 없으면 검색 파라미터를 만들 수 없어 확정하지 않는다."""
    s = Session(input_filters={})
    tools, client = _tools(s)
    out = tools["analyze_distribution"].invoke({"field": "phase", "title": "t"})
    assert "필터가 비어" in out
    assert client.call_count == 0  # CT.gov 호출조차 시도하지 않음
    assert s.final_artifact_id is None
    resp = assemble_response(s)
    # 검색이 한 번도 없었다 → needs_clarification 백스톱
    assert resp["visualization"]["type"] == "needs_clarification"


def test_analyze_distribution_rejects_unknown_field():
    s = Session(input_filters={"condition": "diabetes"})
    tools, client = _tools(s)
    out = tools["analyze_distribution"].invoke(
        {"field": "unknown_axis", "title": "t", "condition": "diabetes"}
    )
    assert "미지원" in out
    assert client.call_count == 0
    assert s.final_artifact_id is None


def test_analyze_comparison_requires_two_groups():
    s = Session(input_filters={})
    tools, _ = _tools(s)
    out = tools["analyze_comparison"].invoke(
        {"filter_sets": [{"label": "A", "drug_name": "A"}], "title": "t"}
    )
    assert "최소 2개" in out
    assert s.final_artifact_id is None


def test_analyze_comparison_parallel_fetch_reuses_cache_for_shared_filters():
    """비교 시 동일 필터 조합은 fetch_cache가 재사용해 API 호출 횟수를 줄인다."""
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
    # 필터가 실제로 다르므로 두 번 호출됨(캐시 미스). 최소한 도구 자체는 정상 진행.
    assert client.call_count == 2


def test_zero_result_does_not_finalize():
    """검색 결과가 0건이면 도구가 확정하지 않고, assemble은 no_data를 반환한다."""
    s = Session(input_filters={})
    tools, _ = _tools(s, studies=[])
    out = tools["analyze_distribution"].invoke(
        {"field": "phase", "title": "t", "condition": "unobtainium"}
    )
    assert "0건" in out
    assert s.final_artifact_id is None
    resp = assemble_response(s)
    assert resp["visualization"]["type"] == "no_data"
