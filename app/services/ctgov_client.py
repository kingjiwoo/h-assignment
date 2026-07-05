"""Thin HTTP client for the ClinicalTrials.gov v2 Data API.

There is no server-side group-by, so this layer only owns pagination and payload
minimization (via the `fields` parameter); the actual aggregation lives in
app/core/aggregate.py.

NOTE: Calls made via httpx consistently produced a 403 from the CT.gov edge (likely
a WAF fingerprinting TLS handshakes — curl and requests both return 200 for the same
request). Rather than spending more time isolating the cause, we switched to the
`requests` library, which works reliably. Documented under README "limitations".
"""

import requests

from app.config import settings

# Superset of fields needed across every analysis type (time_trend/distribution/
# comparison/geo/network). Standardizing on one field list keeps round-trips minimal
# instead of computing a different projection per request.
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
        """Search studies using params (query.*, filter.*, etc.) and return a list of protocolSection dicts.

        Returns:
            (studies, capped) — capped=True means the max_studies cap was hit
            and the full result set was not fetched.
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
