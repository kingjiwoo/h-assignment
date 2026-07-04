"""intent 노드 — 파이프라인에서 유일하게 LLM을 호출하는 지점.

structured output(with_structured_output)으로 Intent 스키마를 강제해, LLM 출력이
항상 검증 가능한 형태가 되도록 한다. trial 수 등 수치는 여기서 절대 만들지 않는다.
"""

from app.graph.state import GraphState, Intent
from app.services.llm import get_chat_model

SYSTEM_PROMPT = """\
너는 임상시험 질문을 구조화된 검색/분석 의도로 변환하는 파서다.

규칙:
- 오직 사용자 질문을 해석해 필드를 채운다. 시험 수·통계 같은 수치는 절대 만들지 마라
  (그건 이후 실제 API 데이터로 계산된다).
- analysis_type은 반드시 다음 중 하나로 결정한다:
  - time_trend: "연도별", "시간에 따라", "추이", "since 20xx" 등 시간 흐름을 물을 때
  - distribution: "phase별 분포", "intervention 유형", "어떻게 나뉘나" 등 한 축의 분포
  - comparison: "A vs B", "두 질환 비교" 등 둘 이상 대상을 나란히 비교
  - geo: "어느 국가", "나라별", "지역" 등 지리적 분포
  - network: "네트워크", "관계", "sponsor-drug", "함께 등장하는 약물(combination)" 등 엔티티 관계망
- distribution이면 distribution_field를 phase(기본)/intervention_type/status 중에서 정한다.
- comparison이면 comparison_groups에 각 대상을 label과 함께 2개 이상 넣는다.
- network면 network_dimension을 sponsor_drug 또는 drug_drug로 정한다
  (combination/약물끼리 함께 쓰이는 관계면 drug_drug, 스폰서-약물 관계면 sponsor_drug).
- 약물명/질환명은 사용자가 쓴 표현을 그대로 둔다. ClinicalTrials.gov 검색엔진이
  브랜드명·동의어·오타를 자체 처리하므로 임의로 표준화하지 마라.
- 확실하지 않은 필드는 null로 둔다.
"""


def intent_node(state: GraphState) -> dict:
    model = get_chat_model().with_structured_output(Intent)
    query = state["query"]
    input_filters = state.get("input_filters", {})

    user_msg = f"질문: {query}"
    if input_filters:
        user_msg += f"\n\n요청에 함께 제공된 구조화 필드(참고용): {input_filters}"

    intent: Intent = model.invoke(
        [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_msg},
        ]
    )
    return {"intent": intent}
