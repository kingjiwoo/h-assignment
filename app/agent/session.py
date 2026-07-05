"""요청 1건 동안 도구들이 공유하는 상태.

에이전트(LLM)가 오케스트레이션하지만, 실제 데이터·수치는 전부 이 Session 안에 도구가 계산해
저장한다. 최종 응답은 LLM 텍스트가 아니라 이 Session의 artifact에서 서버가 직접 조립하므로,
수치가 LLM을 거쳐 전사되며 왜곡될 여지가 없다.
"""

from dataclasses import dataclass, field

from app.core import extractors as ex


@dataclass
class SearchResult:
    label: str
    studies: list[dict]
    capped: bool
    filters: dict


@dataclass
class Artifact:
    """하나의 집계 결과. finalize가 이 중 하나를 최종 시각화로 지목한다."""

    artifact_id: str
    kind: str  # time_trend | distribution | comparison | geo | network
    data: object  # list[dict] 또는 {"nodes":..., "edges":...}
    buckets: dict  # bucket_key -> [nct_id]
    notes: list
    extra: dict = field(default_factory=dict)  # group_labels 등


@dataclass
class Session:
    input_filters: dict = field(default_factory=dict)  # 요청에 명시된 필터 (항상 우선)
    searches: dict = field(default_factory=dict)  # label -> SearchResult
    artifacts: dict = field(default_factory=dict)  # artifact_id -> Artifact
    studies_by_nct: dict = field(default_factory=dict)  # citation 조회용 전역 인덱스
    notes: list = field(default_factory=list)
    final_artifact_id: str | None = None
    final_chart_type: str | None = None
    final_title: str | None = None
    # 에이전트가 "무엇을 조회할지 특정 불가"라고 스스로 선언했을 때 채워진다 (honest abstention 1겹).
    # {"reason": str, "missing": [str, ...]} 형태.
    unresolved: dict | None = None
    _artifact_seq: int = 0

    def index_studies(self, studies: list[dict]) -> None:
        for s in studies:
            self.studies_by_nct[ex.nct_id(s)] = s

    def next_artifact_id(self, kind: str) -> str:
        self._artifact_seq += 1
        return f"{kind}_{self._artifact_seq}"
