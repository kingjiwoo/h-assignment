"""honest abstention (needs_clarification) 단위 테스트 — LLM/네트워크 없이 검증.

1겹(에이전트 자기선언)과 2겹(결정론 백스톱)이 각각 needs_clarification을 만들고,
정상/0건 경로와 올바로 구분되는지 확인한다.
"""

from app.agent.runner import assemble_response
from app.agent.session import Artifact, SearchResult, Session


def test_layer1_report_unresolvable_yields_needs_clarification():
    """1겹: 에이전트가 unresolved를 선언하면 needs_clarification 응답."""
    session = Session(input_filters={})
    session.unresolved = {"reason": "질환·약물이 없습니다", "missing": ["condition", "drug_name"]}

    resp = assemble_response(session)

    assert resp["visualization"]["type"] == "needs_clarification"
    assert resp["clarification"]["reason"] == "질환·약물이 없습니다"
    assert resp["clarification"]["missing"] == ["condition", "drug_name"]
    assert resp["clarification"]["suggestions"]  # 안내 문구가 채워짐


def test_layer2_backstop_no_search_yields_needs_clarification():
    """2겹: unresolved 선언이 없어도, 유효 검색이 0번이면 백스톱이 needs_clarification."""
    session = Session(input_filters={})
    # 검색도 finalize도 없음 (에이전트가 규칙을 어기고 아무것도 안 한 상황)

    resp = assemble_response(session)

    assert resp["visualization"]["type"] == "needs_clarification"
    assert resp["clarification"] is not None


def test_searched_but_zero_results_is_no_data_not_clarification():
    """검색은 했으나 0건이면 no_data (needs_clarification 아님) — 둘을 구분."""
    session = Session(input_filters={"drug_name": "Zzzznonexistent"})
    session.searches["default"] = SearchResult(
        label="default", studies=[], capped=False, filters={"drug_name": "Zzzznonexistent"}
    )

    resp = assemble_response(session)

    assert resp["visualization"]["type"] == "no_data"
    assert resp.get("clarification") is None


def test_normal_finalized_visualization_is_unaffected():
    """정상 경로(검색+집계+finalize)는 needs_clarification과 무관하게 시각화를 반환."""
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
