"""에이전트 실행 + 최종 응답 조립.

흐름: 요청 → create_react_agent(도구=결정론 코어 래퍼) 가 오케스트레이션 →
finalize가 지목한 artifact를 Session에서 꺼내 서버가 QueryResponse를 조립.
수치는 LLM 텍스트를 거치지 않는다.
"""

from langgraph.prebuilt import create_react_agent

from app.agent.session import Artifact, Session
from app.agent.tools import make_tools
from app.core import extractors as ex
from app.services.ctgov_client import CtGovClient
from app.services.llm import get_chat_model

MAX_CITATIONS_PER_BUCKET = 3

SYSTEM_PROMPT = """\
너는 임상시험 질문을 시각화로 답하는 데이터 분석 에이전트다. 다음 도구로만 작업한다:
search_trials → (aggregate_by | compare_groups | build_network) → finalize_visualization.

반드시 지킬 규칙:
0) 질문에서 조회 대상(질환/약물/스폰서/국가 등)을 특정할 수 없거나 너무 모호하면,
   절대 값을 임의로 지어내 검색하지 마라. 대신 report_unresolvable(reason, missing)를 호출하고
   종료하라. "모르겠으면 모른다고 말한다"가 추측보다 우선이다.
   (예: "임상시험 통계 보여줘"처럼 질환·약물 언급이 전혀 없는 경우 → report_unresolvable)
1) 어떤 수치도 네가 직접 만들지 마라. 모든 집계는 도구가 실제 데이터로 계산한다.
   너는 "어떤 검색을 하고 어떤 집계를 조합할지"만 결정한다.
2) 대상을 특정할 수 있으면, 먼저 search_trials로 데이터를 확보한 뒤 집계 도구를 호출한다.
3) 질문 성격에 맞는 집계를 고른다:
   - 연도별 추이 → aggregate_by(field='year') → chart_type='time_series'
   - phase/intervention/status 분포 → aggregate_by(field=...) → 'bar_chart'
   - 국가별 → aggregate_by(field='country') → 'bar_chart'
   - A vs B 비교 → 대상마다 다른 label로 search_trials 여러 번 → compare_groups → 'grouped_bar_chart'
   - 관계망(sponsor↔drug, 병용 약물↔약물) → build_network → 'network_graph'
4) 마지막에 반드시 finalize_visualization(artifact_id, chart_type, title)을 호출해 결과를 확정한다.
5) 검색 결과가 0건이면 억지로 진행하지 말고 그 사실을 설명하며 종료한다(finalize 불필요).
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
