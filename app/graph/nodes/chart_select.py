"""chart_select 노드 — analysis_type과 데이터 형태로 최종 차트 타입을 결정한다.

규칙 기반(결정론적)이다. LLM이 준 analysis_type을 신뢰하되, 데이터가 비면 no_data로 강등한다.
"""

from app.graph.state import GraphState

# 분석 유형 → 기본 차트 타입 매핑
ANALYSIS_TO_CHART = {
    "time_trend": "time_series",
    "distribution": "bar_chart",
    "comparison": "grouped_bar_chart",
    "geo": "bar_chart",
    "network": "network_graph",
}


def _is_empty(analysis_type: str, data) -> bool:
    if not data:
        return True
    if analysis_type == "network":
        return not data.get("nodes")
    return len(data) == 0


def chart_select_node(state: GraphState) -> dict:
    intent = state["intent"]
    aggregated = state.get("aggregated", {})
    data = aggregated.get("data")

    if _is_empty(intent.analysis_type, data):
        return {"chart_type": "no_data"}

    return {"chart_type": ANALYSIS_TO_CHART.get(intent.analysis_type, "bar_chart")}
