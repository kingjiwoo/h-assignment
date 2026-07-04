"""fetch 노드 — CT.gov에서 study 목록을 가져온다. cap과 0건 처리를 담당."""

from app.config import settings
from app.graph.state import GraphState
from app.services.ctgov_client import CtGovClient


def fetch_node(state: GraphState) -> dict:
    client = CtGovClient()
    try:
        studies, capped = client.search_studies(
            state["ctgov_params"], max_studies=settings.max_studies
        )
    finally:
        client.close()
    return {"studies": studies, "capped": capped}
