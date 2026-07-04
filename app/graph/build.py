"""LangGraph StateGraph 조립.

흐름:
    intent → route_by_type
        ├─ comparison → comparison_node ─┐
        └─ 그 외 → query_builder → fetch → aggregate ─┤
                                                        → chart_select → spec_builder → END

라우팅 분기(comparison vs 나머지)는 LLM 재판단이 아니라 intent.analysis_type 값으로만
결정되는 결정론적 conditional edge다.
"""

from langgraph.graph import END, START, StateGraph

from app.graph.nodes.aggregate import aggregate_node
from app.graph.nodes.chart_select import chart_select_node
from app.graph.nodes.comparison import comparison_node
from app.graph.nodes.fetch import fetch_node
from app.graph.nodes.intent import intent_node
from app.graph.nodes.query_builder import query_builder_node
from app.graph.nodes.spec_builder import spec_builder_node
from app.graph.state import GraphState


def _route_by_type(state: GraphState) -> str:
    """comparison만 별도 경로(그룹별 fetch)로, 나머지는 공용 fetch 경로로 보낸다."""
    if state["intent"].analysis_type == "comparison":
        return "comparison"
    return "single"


def build_graph():
    g = StateGraph(GraphState)

    g.add_node("intent", intent_node)
    g.add_node("query_builder", query_builder_node)
    g.add_node("fetch", fetch_node)
    g.add_node("aggregate", aggregate_node)
    g.add_node("comparison", comparison_node)
    g.add_node("chart_select", chart_select_node)
    g.add_node("spec_builder", spec_builder_node)

    g.add_edge(START, "intent")
    g.add_conditional_edges(
        "intent",
        _route_by_type,
        {"comparison": "comparison", "single": "query_builder"},
    )

    # 공용 경로
    g.add_edge("query_builder", "fetch")
    g.add_edge("fetch", "aggregate")
    g.add_edge("aggregate", "chart_select")

    # comparison 경로는 자체 fetch+집계 후 바로 chart_select로 합류
    g.add_edge("comparison", "chart_select")

    g.add_edge("chart_select", "spec_builder")
    g.add_edge("spec_builder", END)

    return g.compile()


# 앱 기동 시 1회 컴파일해 재사용
compiled_graph = build_graph()
