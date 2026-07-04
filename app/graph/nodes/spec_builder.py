"""spec_builder 노드 — visualization 스펙 + meta + citations를 조립한다.

title/encoding은 결정론적으로 만든다(LLM 미사용 → 할루시네이션 방지). 프론트엔드가 추측 없이
렌더링할 수 있도록 차트 타입별 encoding 형태를 명확히 고정한다.
"""

from app.graph import extractors as ex
from app.graph.state import GraphState

MAX_CITATIONS_PER_BUCKET = 3

# 차트 타입별 encoding — README의 응답 스키마 문서와 1:1로 대응한다.
ENCODINGS = {
    "time_series": {"x": {"field": "year", "type": "temporal"}, "y": {"field": "trial_count", "type": "quantitative"}},
    "bar_chart": {"x": {"field": "category", "type": "nominal"}, "y": {"field": "trial_count", "type": "quantitative"}},
    "network_graph": {"nodes": {"id": "id", "group": "kind", "size": "degree"}, "edges": {"source": "source", "target": "target", "weight": "weight"}},
}


def _title(state: GraphState) -> str:
    intent = state["intent"]
    filters = state.get("input_filters", {})
    subject = (
        filters.get("drug_name")
        or intent.drug_name
        or filters.get("condition")
        or intent.condition
        or filters.get("sponsor")
        or intent.sponsor
        or "Clinical trials"
    )
    titles = {
        "time_trend": f"Trials over time for {subject}",
        "distribution": f"Trial distribution by {intent.distribution_field or 'phase'} for {subject}",
        "comparison": f"Comparison of trials: {subject}",
        "geo": f"Trials by country for {subject}",
        "network": f"{'Sponsor–drug' if (intent.network_dimension or 'sponsor_drug') == 'sponsor_drug' else 'Drug–drug'} network for {subject}",
    }
    return titles.get(intent.analysis_type, f"Trials for {subject}")


def _build_encoding(chart_type: str, aggregated: dict) -> dict:
    if chart_type == "grouped_bar_chart":
        return {
            "x": {"field": "category", "type": "nominal"},
            "y": {"field": "<group>", "type": "quantitative"},
            "series": aggregated.get("group_labels", []),
        }
    if chart_type == "bar_chart":
        # geo는 category 대신 country 필드를 쓴다
        first = (aggregated.get("data") or [{}])[0]
        if "country" in first:
            return {"x": {"field": "country", "type": "nominal"}, "y": {"field": "trial_count", "type": "quantitative"}}
    return ENCODINGS.get(chart_type, {})


def _build_citations(state: GraphState) -> dict:
    """각 데이터 버킷 → 근거 study의 nct_id + 정확한 텍스트 발췌(briefTitle)."""
    buckets = state.get("aggregated", {}).get("buckets", {})
    studies_by_nct = {ex.nct_id(s): s for s in state.get("studies", [])}

    citations: dict = {}
    for bucket_key, ncts in buckets.items():
        refs = []
        for nct in ncts[:MAX_CITATIONS_PER_BUCKET]:
            study = studies_by_nct.get(nct)
            if not study:
                continue
            refs.append({"nct_id": nct, "excerpt": ex.brief_title(study)})
        if refs:
            citations[bucket_key] = refs
    return citations


def spec_builder_node(state: GraphState) -> dict:
    chart_type = state["chart_type"]
    intent = state["intent"]
    aggregated = state.get("aggregated", {})
    filters = state.get("input_filters", {})

    notes = []
    if intent.notes:
        notes.append(intent.notes)
    notes.extend(aggregated.get("notes", []))
    if state.get("capped"):
        notes.append(
            f"결과가 상한(MAX_STUDIES)에 걸려 최근/상위 일부 study만 집계했습니다. "
            f"수치는 전체가 아닌 표본 기준입니다."
        )

    if chart_type == "no_data":
        return {
            "visualization": {
                "type": "no_data",
                "title": _title(state),
                "encoding": {},
                "data": [],
            },
            "meta": {
                "filters": {**filters},
                "analysis_type": intent.analysis_type,
                "source": "clinicaltrials.gov",
                "study_count": len(state.get("studies", [])),
                "capped": bool(state.get("capped")),
                "notes": notes + ["조건에 맞는 시험을 찾지 못했습니다."],
            },
            "citations": None,
        }

    visualization = {
        "type": chart_type,
        "title": _title(state),
        "encoding": _build_encoding(chart_type, aggregated),
        "data": aggregated.get("data", []),
    }
    meta = {
        "filters": {**filters},
        "analysis_type": intent.analysis_type,
        "source": "clinicaltrials.gov",
        "study_count": len(state.get("studies", [])),
        "capped": bool(state.get("capped")),
        "notes": notes,
    }
    return {"visualization": visualization, "meta": meta, "citations": _build_citations(state) or None}
