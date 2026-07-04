# ClinicalTrials.gov Query-to-Visualization Agent (Backend)

자연어 임상시험 질문을 받아 [ClinicalTrials.gov v2 API](https://clinicaltrials.gov/data-api/api)에서 실제 데이터를 조회·집계하고, 프론트엔드가 그대로 렌더링할 수 있는 **구조화된 시각화 스펙(JSON)**을 반환하는 백엔드 서비스입니다.

- **Stack:** Python 3.11+, FastAPI, LangGraph, Pydantic
- **지원 시각화:** `time_series`, `bar_chart`, `grouped_bar_chart`, `network_graph` (+ 빈 결과용 `no_data`)
- **지원 질문 유형:** 시간 추세 · 분포 · 비교 · 지리적 분포 · 관계망(network)
- **보너스:** 각 데이터 포인트에 근거 `nct_id` + 실제 API 텍스트 발췌를 붙이는 Deep Citations

---

## 1. 빠른 시작 (Run)

### 설치
```bash
# uv 사용 (권장)
uv sync

# 또는 pip
pip install -e .
```

### 설정
```bash
cp .env.example .env
# .env를 열어 ANTHROPIC_API_KEY 또는 OPENAI_API_KEY 중 하나 이상 입력
```

| 환경변수 | 필수 | 설명 |
|---|---|---|
| `ANTHROPIC_API_KEY` | 둘 중 하나 | Anthropic 사용 시 |
| `OPENAI_API_KEY` | 둘 중 하나 | OpenAI 사용 시 |
| `LLM_PROVIDER` | 선택 | `anthropic`\|`openai` 명시(미지정 시 키 존재로 자동 선택, Anthropic 우선) |
| `LLM_MODEL` | 선택 | 모델명 override |
| `MAX_STUDIES` | 선택 | 요청당 CT.gov에서 가져올 study 상한(기본 500) |

### 서버 실행
```bash
uv run uvicorn app.main:app --reload
# http://localhost:8000/docs 에서 Swagger UI로 시험 가능
```

### 호출 예시
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "How are diabetes trials distributed across phases?", "condition": "diabetes"}'
```

### 테스트 / 예시 재생성
```bash
uv run pytest                                   # 집계·쿼리빌더 단위테스트(네트워크·LLM 불필요)
PYTHONPATH=. uv run python scripts/run_examples.py   # examples/example_runs.md 재생성
```

---

## 2. 요청 스키마 (Request)

`POST /query`, `Content-Type: application/json`. `query`만 필수이며 나머지는 선택 필터입니다.
**명시적으로 전달된 필터는 LLM이 자연어에서 추출한 값보다 항상 우선 적용됩니다**(결정론적 병합 규칙).

| 필드 | 타입 | 필수 | 설명 / 검증 |
|---|---|---|---|
| `query` | string | ✅ | 자연어 질문 (min length 1) |
| `drug_name` | string | ❌ | 중재/약물명. 예: `Pembrolizumab` |
| `condition` | string | ❌ | 질환명. 예: `breast cancer` |
| `sponsor` | string | ❌ | 스폰서명 |
| `country` | string | ❌ | 국가명. 예: `Canada` |
| `trial_phase` | string | ❌ | `EARLY_PHASE1`\|`PHASE1`\|`PHASE2`\|`PHASE3`\|`PHASE4`\|`NA` |
| `start_year` | int | ❌ | 시작 연도(inclusive) |
| `end_year` | int | ❌ | 종료 연도(inclusive) |

Pydantic(`app/schemas.py`)이 타입·필수여부를 검증하며, 위반 시 FastAPI가 422를 반환합니다.

---

## 3. 응답 스키마 (Response)

```jsonc
{
  "visualization": {
    "type": "bar_chart",          // time_series | bar_chart | grouped_bar_chart | network_graph | no_data
    "title": "사람이 읽을 수 있는 제목",
    "encoding": { ... },           // 아래 타입별 표 참고
    "data": [ ... ] | { ... }      // 아래 타입별 표 참고
  },
  "meta": {
    "filters": { ... },            // 요청에 명시된 필터 에코백
    "analysis_type": "distribution",
    "source": "clinicaltrials.gov",
    "study_count": 300,            // 집계에 사용된 study 수
    "capped": true,               // MAX_STUDIES 상한에 걸렸는지
    "notes": [ "..." ]             // 가정·필터·절삭 등 사람이 읽는 노트
  },
  "citations": {                   // (보너스) 없으면 null
    "<bucket_key>": [ { "nct_id": "NCT...", "excerpt": "API 응답의 정확한 발췌" } ]
  }
}
```

### 차트 타입별 `encoding` / `data` 형태

| type | encoding | data |
|---|---|---|
| `time_series` | `{x:{field:"year",type:"temporal"}, y:{field:"trial_count",type:"quantitative"}}` | `[{year, trial_count}]` |
| `bar_chart` (분포) | `{x:{field:"category"}, y:{field:"trial_count"}}` | `[{category, trial_count}]` |
| `bar_chart` (지리) | `{x:{field:"country"}, y:{field:"trial_count"}}` | `[{country, trial_count}]` |
| `grouped_bar_chart` | `{x:{field:"category"}, y:{field:"<group>"}, series:[라벨...]}` | `[{category, "<라벨1>":n, "<라벨2>":n}]` |
| `network_graph` | `{nodes:{id,group,size}, edges:{source,target,weight}}` | `{nodes:[{id,kind,degree}], edges:[{source,target,weight}]}` |
| `no_data` | `{}` | `[]` |

### Citations `bucket_key` 규칙
- 분포/시간/지리: 데이터 포인트의 카테고리 값 (예: `"PHASE3"`, `"2020"`, `"Canada"`)
- 비교: `"<그룹라벨>|<카테고리>"` (예: `"Nivolumab|PHASE2"`)
- 네트워크: `"<source>|<target>"` (예: `"Merck Sharp & Dohme LLC|Pembrolizumab"`)

버킷당 최대 3개 citation으로 제한합니다.

---

## 4. 아키텍처 & 설계 결정

### 파이프라인 (LangGraph `StateGraph`)

```
POST /query
   │
   ▼
[intent]  ← 파이프라인에서 유일한 LLM 호출 (structured output으로 Intent 스키마 강제)
   │
   ├─ analysis_type == "comparison" ─▶ [comparison] ─┐  (그룹별로 별도 조회+집계)
   │                                                  │
   └─ 그 외 ─▶ [query_builder] ─▶ [fetch] ─▶ [aggregate] ─┤
                                                           ▼
                                              [chart_select] ─▶ [spec_builder] ─▶ 응답
```

각 노드 책임:
- **intent** (`graph/nodes/intent.py`): 자연어 → `Intent`(필터 + `analysis_type` + 분석별 옵션). LLM은 여기서만, 오직 "해석"만 담당.
- **query_builder**: `Intent`+명시 필터 → CT.gov query params. 순수 결정론.
- **fetch**: `pageSize=1000`+`pageToken` 페이징, `MAX_STUDIES` cap, 필요한 `fields`만 요청.
- **aggregate**: 5개 순수 집계 함수(time_trend/distribution/comparison/geo/network).
- **comparison**: 그룹마다 다른 필터로 별도 조회가 필요해 자체 fetch+집계.
- **chart_select**: `analysis_type`+데이터 형태로 최종 차트 타입 결정(빈 데이터는 `no_data`로 강등).
- **spec_builder**: `visualization`+`meta`(+`citations`) 조립. 제목/encoding은 결정론적으로 생성.

### 핵심 설계 원칙과 트레이드오프

**1) 할루시네이션이 불가능한 구조 (AI/Agent Design 배점 정면 대응)**
LLM은 자연어를 `Intent`로 해석하는 **단 한 지점**에만 개입하며, `with_structured_output`으로 Pydantic 스키마가 강제됩니다. **trial 수 등 모든 수치는 LLM이 아니라 실제 API 응답을 코드로 집계**해서 만듭니다. 즉 LLM이 숫자를 지어낼 경로 자체가 존재하지 않습니다.

**2) 싱글 에이전트 + 도구/노드 래핑 (멀티에이전트 아님)**
5개 분석 유형은 전부 "study 목록 → group-by/count/edge"라는 **동일 패턴의 변형**입니다. 서로 다른 전문 지식이 필요하지 않으므로 멀티에이전트(supervisor)는 비용·지연만 늘리고 정확도 이득이 없다고 판단했습니다. 라우팅은 LLM 재판단이 아니라 `analysis_type` 값에 따른 **결정론적 conditional edge**입니다.

**3) 엔티티 이름 교정 계층을 의도적으로 넣지 않음**
초기 설계에서 `resolve_drug_name` 같은 브랜드명/오타 교정 tool을 고려했으나, 실측으로 **CT.gov 검색엔진(Essie)이 브랜드명(`Keytruda`→Pembrolizumab)·오타(`pembrolizumb`)·동의어(`heart attack`)를 이미 자체 처리**함을 확인했습니다. API가 잘 하는 일을 LLM tool로 재구현하는 것은 과잉설계이므로 제외했습니다.

**4) 서버사이드 group-by 부재에 대한 대응**
CT.gov는 `stats/field/values`(Phase 등 일부 enum) 외에는 서버 집계를 제공하지 않습니다. 따라서 필터 범위 내 study를 받아와 메모리에서 집계하되, **`MAX_STUDIES` 상한**을 두고 초과 시 `meta.capped=true`와 노트로 "표본 기준"임을 정직하게 표기합니다.

**5) 프론트 친화적 스펙 + 응답 크기 관리**
network는 가중치 상위 60개 엣지, geo는 상위 25개 국가로 제한하고 절삭 사실을 `meta.notes`에 남깁니다. 무한히 큰 그래프 대신 "허브 중심의 의미있는 관계망"을 반환합니다.

### 확장 방법
- **새 분석 유형 추가:** `Intent.analysis_type`에 값 추가 → `aggregate.py`에 순수 집계 함수 1개 추가 → `chart_select`의 매핑 1줄 추가. 다른 계층은 건드릴 필요 없음.
- **새 필터 추가:** `schemas.QueryRequest`·`Intent`에 필드 추가 → `query_builder.build_ctgov_params`에 매핑 1줄.

---

## 5. 검증 방법 (How I Validated Correctness)

- **집계 로직 단위테스트** (`tests/`, 12개): 오프라인 fixture(`tests/fixtures/sample_studies.json`)로 5개 집계 함수와 query_builder를 네트워크·LLM 없이 검증. 국가 study-단위 dedupe, phase 미지정→`NA` 정규화, 네트워크 엣지 weight, comparison 축 정렬 등 경계 케이스 포함.
- **실 API 통합 검증** (`scripts/run_examples.py`): 6개 예시(5개 카테고리 + 빈 결과)를 **실제 ClinicalTrials.gov API**에 대해 실행하고 결과를 `examples/example_runs.md`에 기록. 네트워크 그래프가 실제 허브 스폰서(NCI·Merck 등)와 약물을 연결하는지, citation의 `nct_id`+발췌가 실제 study와 일치하는지 육안 확인.
- **API 계약 사전 실측:** 구현 전 `curl`로 필드셋·`filter.advanced`(phase/date range)·`query.locn`(country)·페이지네이션·최대 pageSize를 직접 검증한 뒤 클라이언트를 작성.

---

## 6. 한계점 & 개선 방향 (Limitations / With More Time)

- **`MAX_STUDIES` 표본 편향:** 상한을 넘는 쿼리는 관련도 정렬 상위 N건만 집계하므로, 특히 time_trend가 전체 census가 아닌 표본이 됩니다(`capped`로 표기). → 개선: time_trend는 연도별로 `countTotal`을 나눠 질의해 정확한 전수 집계.
- **HTTP 클라이언트:** `httpx`로 호출 시 CT.gov 엣지에서 일관되게 403이 발생(TLS 지문 차이로 추정)하여 `requests`로 전환했습니다. 원인 정밀 분석은 시간상 보류.
- **LLM 실경로 예시:** 제출 환경에 API 키가 없어 `example_runs.md`는 intent만 주입하고 **데이터·집계·스펙은 실제 코드로 생성**한 결과입니다(각 문서에 모드 명시). 키를 넣으면 동일 스크립트가 intent 노드 포함 전체 그래프로 실행됩니다.
- **국가 필터 정밀도:** `query.locn`은 텍스트 검색이라 지역명 동음이의에 민감할 수 있습니다. → 개선: geo 좌표/표준 국가코드 기반 필터.
- **캐싱/레이트리밋:** 동일 쿼리 반복 시 CT.gov 재호출. → 개선: 결과 캐시 + 재시도/백오프.

---

## 7. AI 도구 사용 내역 (Integrity Note)

- **사용 도구:** Claude Code(본 구현의 페어 프로그래밍/코드 생성)와 웹 검색(LangGraph 싱글 vs 멀티에이전트 트레이드오프 조사).
- **직접 설계한 부분(deliberate design):** 전체 아키텍처와 노드 분해, "LLM은 intent 해석에만·수치는 코드 집계" 원칙, 싱글에이전트 선택 근거, 이름 교정 계층 제외 결정, 응답 스키마·citation 버킷 키 규칙, `MAX_STUDIES`/top-N 절삭 같은 정직성 장치.
- **생성 후 검증·조정한 부분(generated & adapted):** 집계 함수·클라이언트·노드의 보일러플레이트 코드, 테스트 케이스. 모든 API 가정(필드명, `filter.advanced` 문법, pageSize 한계, Essie의 브랜드명/오타 처리)은 **코드 작성 전에 `curl`로 실측**해 확인했고, 집계 정확성은 단위테스트와 실 API 결과 육안 검증으로 확인했습니다.
