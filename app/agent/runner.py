"""에이전트 실행 + 최종 응답 조립.

흐름: 요청 → create_react_agent(도구=결정론 코어 래퍼) 가 오케스트레이션 →
finalize가 지목한 artifact를 Session에서 꺼내 서버가 QueryResponse를 조립.
수치는 LLM 텍스트를 거치지 않는다.
"""

from langgraph.prebuilt import create_react_agent

from app.agent.session import Artifact, Session
from app.agent.tools import KIND_TO_CHART, make_tools
from app.core import extractors as ex
from app.services.ctgov_client import CtGovClient
from app.services.llm import get_chat_model

MAX_CITATIONS_PER_BUCKET = 3

SYSTEM_PROMPT = """\
너는 임상시험 질문을 시각화로 답하는 데이터 분석 에이전트다.

정확히 하나의 도구를 골라 호출해 결과를 확정한다:
- analyze_time_trend    — 연도별 시험 수 추이 (time_series)
- analyze_distribution  — phase/intervention_type/status/country 분포 (bar_chart)
- analyze_comparison    — 두 개 이상 대상의 나란한 비교 (grouped_bar_chart)
- analyze_network       — sponsor↔drug 또는 drug↔drug 관계망 (network_graph)
- report_unresolvable   — 조회 대상을 특정할 수 없을 때 (honest abstention)

규칙:
0) 질문에서 조회 대상(질환/약물/스폰서/국가 등)을 특정할 수 없거나 너무 모호하면,
   임의로 값을 지어내지 말고 report_unresolvable(reason, missing)을 호출하고 종료한다.
   "모르겠으면 모른다"가 추측보다 우선이다.
1) 각 analyze_* 도구는 내부에서 검색→집계→차트 확정까지 원자적으로 수행한다.
   한 질문에는 원칙적으로 도구를 한 번만 호출한다. 추가 호출은 결과를 덮어쓴다.
2) 어떤 수치도 네가 직접 만들지 마라. 도구가 실제 데이터로 계산한다.
3) 검색 결과가 0건이거나 필터 부족 오류가 나오면, 다른 도구를 억지로 호출하지 말고 종료한다.
4) 비교는 analyze_comparison(filter_sets=[{label,...필터}, ...], field='phase'|'status')로 한다.
   여러 번의 analyze_distribution 호출로 흉내 내지 말 것.
"""

# 차트 타입별 encoding — 프론트가 추측 없이 렌더링하도록 고정.
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
        "visualization": {"type": "no_data", "title": "결과 없음", "encoding": {}, "data": []},
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


# missing 항목별로 사용자에게 안내할 후보 문구.
_SUGGESTION_MAP = {
    "condition": "질환명을 알려주세요 (예: 'melanoma', 'diabetes').",
    "drug_name": "약물/중재명을 알려주세요 (예: 'Pembrolizumab').",
    "sponsor": "스폰서명을 알려주세요.",
    "country": "국가명을 알려주세요 (예: 'Canada').",
}


def _needs_clarification_response(session: Session, reason: str, missing: list[str]) -> dict:
    """무엇을 조회할지 특정할 수 없을 때의 응답 (honest abstention).

    no_data(조회했으나 0건)와 구분되는 별도 종료 상태. 사용자에게 무엇이 부족한지,
    무엇을 추가하면 되는지 clarification 필드로 알려준다.
    """
    suggestions = [_SUGGESTION_MAP[m] for m in missing if m in _SUGGESTION_MAP]
    if not suggestions:
        suggestions = ["질환·약물·스폰서·국가 중 하나 이상을 질문에 포함해 주세요."]
    return {
        "visualization": {
            "type": "needs_clarification",
            "title": "질문을 특정할 수 없습니다",
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
    """Session 상태(도구가 채운 artifact)로부터 최종 QueryResponse dict를 조립한다.

    LLM과 무관한 순수 조립 단계라 오프라인에서도 테스트/재사용 가능하다.
    """
    # 1겹: 에이전트가 "특정 불가"를 스스로 선언한 경우 (추측 대신 정직한 기권).
    if session.unresolved:
        return _needs_clarification_response(
            session,
            session.unresolved.get("reason") or "질문에서 조회 대상을 특정할 수 없습니다.",
            session.unresolved.get("missing") or [],
        )

    if not session.final_artifact_id:
        # 2겹(결정론 백스톱): LLM이 규칙을 어겨 report_unresolvable를 안 불렀더라도,
        # 유효한 검색이 한 번도 없었다면 = 조회 대상을 특정하지 못한 것 → needs_clarification.
        if not session.searches:
            return _needs_clarification_response(
                session,
                "질문에서 어떤 임상시험을 조회할지 특정할 수 없습니다.",
                ["condition", "drug_name", "sponsor"],
            )
        # 검색은 했으나 결과가 0건 → no_data (조회 대상은 정해졌으나 데이터가 없음).
        if _total_studies(session) == 0:
            return _no_data_response(session, "조건에 맞는 시험을 찾지 못했습니다.")
        # 검색 결과는 있으나 시각화를 확정하지 못함 (에이전트 미완).
        return _no_data_response(session, "에이전트가 시각화를 확정하지 못했습니다.")

    artifact = session.artifacts[session.final_artifact_id]
    chart_type = session.final_chart_type

    # 안전벨트: 도구가 kind에서 chart_type을 결정하므로 정상 경로에선 어긋날 일이 없지만,
    # 세션 직접 조작 등 우회 경로에 대비해 최종 조립 시 한 번 더 방어한다.
    # 어긋난 상태로 통과되면 encoding이 data 키와 맞지 않아 프론트가 렌더 불가.
    expected_chart = KIND_TO_CHART.get(artifact.kind)
    if expected_chart is None or chart_type != expected_chart:
        return _no_data_response(
            session,
            f"내부 정합성 오류: artifact.kind='{artifact.kind}'와 chart_type='{chart_type}'가 맞지 않습니다.",
        )

    # 집계 결과가 실질적으로 비어있으면 빈 차트 대신 no_data로 강등 (list와 dict 양쪽 처리).
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
        return _no_data_response(session, "집계 결과가 비어 있습니다.")

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
    """전체 실행: LLM 에이전트가 도구를 오케스트레이션한 뒤 응답을 조립한다."""
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
