"""ClinicalTrials.gov v2 Data API에 대한 얇은 HTTP 클라이언트.

서버사이드 group-by가 없으므로, 여기서는 페이지네이션과 payload 최소화(fields 파라미터)만
책임지고 집계는 app/graph/nodes/aggregate.py가 담당한다.

NOTE: httpx로 호출 시 CT.gov 엣지(WAF로 추정)에서 일관되게 403이 발생하는 것을 확인했다
(TLS handshake 지문 차이로 추정 — curl과 requests는 동일 요청이 200을 반환). 원인 분석에
시간을 더 쓰기보다 안정적으로 동작하는 requests로 전환했다. README 한계점에 기록.
"""

import requests

from app.config import settings

# 모든 분석 타입(time_trend/distribution/comparison/geo/network)이 공통으로 필요로 하는
# 필드의 상위집합. 요청마다 다른 fields 조합을 짜는 대신 하나로 통일해 왕복 횟수를 줄인다.
STUDY_FIELDS = [
    "NCTId",
    "BriefTitle",
    "OverallStatus",
    "StartDate",
    "Phase",
    "LeadSponsorName",
    "CollaboratorName",
    "Condition",
    "InterventionName",
    "InterventionType",
    "LocationCountry",
]


class CtGovClient:
    def __init__(self, base_url: str | None = None, timeout: float = 20.0) -> None:
        self.base_url = base_url or settings.ctgov_base_url
        self.timeout = timeout
        self._session = requests.Session()

    def search_studies(self, params: dict, max_studies: int) -> tuple[list[dict], bool]:
        """params(query.*, filter.* 등)로 study를 검색해 protocolSection dict 리스트를 반환한다.

        Returns:
            (studies, capped) — capped=True면 max_studies 제한에 걸려 전체 결과를 다 가져오지 못한 것.
        """
        studies: list[dict] = []
        page_token: str | None = None
        capped = False

        while len(studies) < max_studies:
            page_size = min(1000, max_studies - len(studies))
            request_params = {
                **params,
                "fields": ",".join(STUDY_FIELDS),
                "pageSize": page_size,
            }
            if page_token:
                request_params["pageToken"] = page_token

            resp = self._session.get(
                f"{self.base_url}/studies", params=request_params, timeout=self.timeout
            )
            resp.raise_for_status()
            body = resp.json()

            for study in body.get("studies", []):
                studies.append(study.get("protocolSection", {}))

            page_token = body.get("nextPageToken")
            if not page_token:
                break

        if page_token and len(studies) >= max_studies:
            capped = True

        return studies, capped

    def close(self) -> None:
        self._session.close()
