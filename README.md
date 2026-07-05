# ClinicalTrials.gov Query-to-Visualization Agent (Backend)

자연어 임상시험 질문을 받아 [ClinicalTrials.gov v2 API](https://clinicaltrials.gov/data-api/api)에서 실제 데이터를 조회·집계하고, 프론트엔드가 그대로 렌더링할 수 있는 **구조화된 시각화 스펙(JSON)**을 반환하는 백엔드 서비스입니다.

- **Stack:** Python 3.11+, FastAPI, LangGraph(`create_react_agent`), Pydantic
- **에이전트 구조:** LLM이 도구를 오케스트레이션하는 ReAct 에이전트. 단, **모든 수치는 결정론적 도구가 계산**하고 LLM은 숫자를 만들지 않는다.
- **지원 시각화:** `time_series`, `bar_chart`, `grouped_bar_chart`, `network_graph` (+ 빈 결과용 `no_data`)
- **지원 질문 유형:** 시간 추세 · 분포 · 비교 · 지리적 분포 · 관계망(network)
- **보너스:** 각 데이터 포인트에 근거 `nct_id` + 실제 API 텍스트 발췌를 붙이는 Deep Citations

---

## 1. 빠른 시작 (Run)

```bash
uv sync                       # 또는: pip install -e .
cp .env.example .env          # ANTHROPIC_API_KEY 또는 OPENAI_API_KEY 중 하나 입력
uv run uvicorn app.main:app --reload
# http://localhost:8000/docs 에서 Swagger UI 사용
```

| 환경변수 | 필수 | 설명 |
|---|---|---|
| `ANTHROPIC_API_KEY` | 둘 중 하나 | Anthropic 사용 시 |
| `OPENAI_API_KEY` | 둘 중 하나 | OpenAI 사용 시 |
| `LLM_PROVIDER` | 선택 | `anthropic`\|`openai` (미지정 시 키 존재로 자동 선택, Anthropic 우선) |
| `LLM_MODEL` | 선택 | 모델명 override |
| `MAX_STUDIES` | 선택 | 요청당 CT.gov에서 가져올 study 상한(기본 500) |

### 호출 예시
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Show a network of sponsors and drugs for melanoma trials.", "condition": "melanoma"}'
```

### 테스트 / 예시 재생성
```bash
uv run pytest                                        # 집계·도구·조립 단위/통합 테스트(네트워크·LLM 불필요)
PYTHONPATH=. uv run python scripts/run_examples.py   # examples/example_runs.md 재생성
```

### 프론트엔드 (선택) — 채팅형 UI
백엔드와 별도로 `frontend/`에 Next.js 15 SPA가 포함되어 있어, 5개 시각화 타입을
브라우저에서 바로 확인할 수 있습니다. 자세한 내용은 [`frontend/README.md`](./frontend/README.md).
```bash
cd frontend && pnpm install && pnpm dev              # :3000 → 백엔드 :8000 호출
```

---

## 2. 요청 스키마 (Request)

`POST /query`, `Content-Type: application/json`. `query`만 필수이며 나머지는 선택 필터입니다.
**명시적으로 전달된 필터는 에이전트가 자연어에서 판단한 값보다 항상 우선 적용됩니다**(도구 계층에서 결정론적으로 병합).

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
    "type": "network_graph",       // time_series | bar_chart | grouped_bar_chart | network_graph | no_data
    "title": "사람이 읽을 수 있는 제목",
    "encoding": { ... },            // 아래 타입별 표 참고
    "data": [ ... ] | { ... }       // 아래 타입별 표 참고
  },
  "meta": {
    "filters": { ... },             // 요청에 명시된 필터 에코백
    "analysis_type": "network",     // time_trend|distribution|comparison|geo|network|null
    "source": "clinicaltrials.gov",
    "study_count": 300,             // 집계에 사용된 study 수
    "capped": true,                // MAX_STUDIES 상한에 걸렸는지
    "notes": [ "..." ]              // 가정·필터·절삭 등 사람이 읽는 노트
  },
  "citations": {                    // (보너스) 없으면 null
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
- 비교: `"<그룹라벨>|<카테고리>"` (예: `"nivo|PHASE2"`)
- 네트워크: `"<source>|<target>"` (예: `"Merck Sharp & Dohme LLC|Pembrolizumab"`)

버킷당 최대 3개 citation으로 제한합니다.

---

## 4. 아키텍처 & 설계 결정

### 구조: "통제된 ReAct 에이전트"

LLM이 도구를 **오케스트레이션**(어떤 검색을 하고 어떤 집계를 조합할지)하되, **모든 수치는 결정론적
도구가 계산**합니다. 자세한 다이어그램은 [`docs/architecture.md`](docs/architecture.md).

```
POST /query
   │
   ▼
create_react_agent (LLM)  ──▶ 도구 호출 루프 (LLM이 순서·조합 결정)
   │
   ├─ search_trials(filters, label)      : CT.gov 검색 → Session에 저장 (수치 계산 아님)
   ├─ aggregate_by(field, label)         : year/phase/type/status/country group-by count
   ├─ compare_groups(labels, field)      : 여러 검색을 같은 축으로 비교 (grouped bar)
   ├─ build_network(dimension, label)    : sponsor↔drug / drug↔drug 관계망
   └─ finalize_visualization(id, type, title) : 최종 시각화 확정
   │
   ▼
서버가 Session의 artifact(도구가 계산한 실제 데이터)로 QueryResponse 조립
```

**핵심 안전장치 — 숫자는 LLM을 거치지 않는다:**
도구는 실제 수치를 `app/core`(집계 코어)로 계산해 **Session에 저장**하고, LLM에는 요약(preview)만
반환합니다. 최종 응답은 LLM이 쓴 텍스트가 아니라 **서버가 Session에 저장된 artifact에서 직접 꺼내**
조립합니다. 즉 LLM이 trial 수를 지어내거나 전사 오류를 낼 경로가 구조적으로 없습니다.

### 계층 구성
| 계층 | 위치 | 책임 |
|---|---|---|
| API | `app/main.py` | FastAPI, 요청 검증, 명시 필터 추출 |
| 오케스트레이션 | `app/agent/` | `runner`(에이전트 실행+응답 조립), `tools`(도구), `session`(요청 상태) |
| 계산 코어 | `app/core/` | `aggregate`(5개 순수 집계), `extractors`(필드 추출), `query`(파라미터 빌드) — **LLM 무관, 전량 단위테스트** |
| 외부 연동 | `app/services/` | `ctgov_client`(CT.gov HTTP), `llm`(provider-agnostic) |

### 핵심 설계 결정과 트레이드오프

**1) 왜 ReAct 에이전트(`create_react_agent`)인가 — 확장성**
질문 유형을 코드에 하드코딩(고정 switch)하면 새 질문 클래스마다 코드 변경이 필요해 확장성이 떨어집니다.
에이전트가 도구를 **런타임에 조합**하게 하면, 명시적으로 배선하지 않은 조합(예: 특정 필터+특정 집계)이나
장차 멀티스텝 질문("상위 스폰서를 찾고 → 그들의 추이를 보라")까지 **코드 변경 없이** 확장할 수 있습니다.

**2) 그러나 "숫자 생성"은 절대 위임하지 않음 — 할루시네이션 방지**
ReAct의 위험은 LLM이 수치를 지어내는 것입니다. 그래서 집계·카운트는 전부 `app/core`의 순수 함수(도구)로
가두고, LLM은 "판단"(도구 선택·필터 추출·제목 생성)에만 관여합니다. 도구가 계산한 값은 Session에 저장돼
LLM 텍스트를 우회해 응답에 실립니다. → 채점 기준 "avoid hallucination-prone steps / validation·constraints"에 대응.

**3) 결정론적 코어 재사용 — 테스트 용이성**
5개 집계 함수는 실제로 "범용 group-by-count + network 특수케이스"입니다. 이를 `app/core`에 순수 함수로
두어 오케스트레이션(에이전트)과 분리했고, 네트워크·LLM 없이 fixture만으로 전량 단위테스트합니다.
오케스트레이션을 그래프↔에이전트로 바꿔도 이 코어와 테스트는 불변입니다.

**4) 엔티티 이름 교정 계층을 의도적으로 넣지 않음**
CT.gov 검색엔진(Essie)이 브랜드명(`Keytruda`→Pembrolizumab)·오타(`pembrolizumb`)·동의어(`heart attack`)를
이미 처리함을 실측 확인 → 별도 교정 도구는 과잉설계로 제외.

**5) 실 API 데이터의 sensible 처리 — cap & top-N**
서버사이드 group-by가 없어 필터 범위 내 study를 받아 메모리 집계하되, `MAX_STUDIES` 상한을 두고 초과 시
`meta.capped=true`+노트로 "표본 기준"임을 표기합니다. network는 상위 60엣지, geo는 상위 25국으로 절삭하고
절삭 사실을 노트에 남겨 "허브 중심의 의미있는 관계망"을 반환합니다.

### 확장 방법
- **새 집계 축 추가:** `aggregate_by`의 `field` 목록에 값 추가 + `app/core/aggregate`에 매핑. 도구 시그니처 유지 → 에이전트가 자동 활용.
- **새 도구 추가:** `app/agent/tools.py`에 `@tool` 하나 추가 → 에이전트가 프롬프트만으로 조합 가능.

---

## 5. 검증 방법 (How I Validated Correctness)

- **계산 코어 단위테스트** (`tests/test_aggregate.py`, `test_query_builder.py`): fixture로 5개 집계와 파라미터 빌드를 검증. study 단위 국가 dedupe, phase 미지정→`NA`, 네트워크 엣지 weight, comparison 축 정렬 등 경계 포함.
- **에이전트 도구+조립 통합테스트** (`tests/test_agent_flow.py`): 가짜 클라이언트(fixture)로 도구를 순서대로 호출해 조립 결과·citation·**명시 필터 우선 규칙**·no_data·가드(검색 없이 집계 시도)를 검증. LLM/네트워크 불필요.
- **실 API 통합 검증** (`scripts/run_examples.py`): 6개 예시(5개 카테고리+빈 결과)를 실제 CT.gov API로 실행해 `examples/example_runs.md`에 기록. 네트워크가 실제 허브 스폰서(NCI·Merck 등)를 연결하는지, citation의 `nct_id`+발췌가 실제 study와 일치하는지 확인.
- **API 계약 사전 실측:** 구현 전 `curl`로 필드셋·`filter.advanced`(phase/date range)·`query.locn`·페이지네이션·최대 pageSize를 직접 확인.

**전체 테스트 17개 통과** (`uv run pytest`).

---

## 6. 한계점 & 개선 방향 (Limitations / With More Time)

- **`MAX_STUDIES` 표본 편향:** 상한 초과 쿼리는 관련도 상위 N건만 집계하므로 특히 time_trend가 전수 census가 아닌 표본이 됩니다(`capped` 표기). → 개선: time_trend는 연도별 `countTotal` 분할 질의로 정확 집계.
- **멀티홉 질문 미구현:** 현재 프롬프트/예시는 단일홉 위주입니다. 에이전트 구조라 "상위 스폰서→그들의 추이" 같은 멀티홉이 원리적으로 가능하지만 전용 도구/검증은 시간상 보류. → 개선: 중간 결과를 다음 검색에 넣는 도구 추가 + 무한루프 방지 강화.
- **HTTP 클라이언트:** `httpx` 호출 시 CT.gov 엣지에서 일관된 403(TLS 지문 추정)이 발생해 `requests`로 전환. 원인 정밀 분석은 보류.
- **LLM 실경로 예시:** 제출 환경에 API 키가 없어 `example_runs.md`는 `scripted` 모드(도구 시퀀스 재현)로 생성했습니다. 데이터·집계·조립은 실제 코드/API 결과이며, 키를 넣으면 동일 스크립트가 `run_agent`(실제 에이전트)로 실행됩니다.
- **에이전트 비결정성:** ReAct는 도구 선택이 매 실행 달라질 수 있습니다. 수치 정확성은 도구가 보장하지만, "선택된 차트 타입"은 달라질 수 있어 프롬프트로 유도만 합니다. → 개선: 도구 선택에 대한 사후 검증/평가 셋.

---

## 7. AI 도구 사용 내역 (Integrity Note)

- **사용 도구:** Claude Code(페어 프로그래밍/코드 생성), 웹 검색(LangGraph 싱글 vs 멀티에이전트·ReAct 트레이드오프 조사).
- **직접 설계·판단한 부분(deliberate):** 전체 아키텍처, "LLM은 오케스트레이션만·수치는 도구가 계산·응답은 Session artifact에서 조립" 원칙, ReAct 채택 근거와 그 위험(숫자 생성)을 봉쇄하는 방식, 이름 교정 계층 제외, 응답 스키마·citation 버킷 키 규칙, cap/top-N 정직성 장치. (초기엔 결정론적 그래프로 구현했다가, 확장성 관점을 반영해 ReAct 에이전트로 리팩터링하며 계산 코어는 그대로 재사용.)
- **생성 후 검증·조정한 부분(generated & adapted):** 도구/클라이언트/집계의 보일러플레이트, 테스트 케이스. 모든 API 가정은 코드 작성 전에 `curl`로 실측했고, 정확성은 단위·통합 테스트와 실 API 결과 육안 검증으로 확인.
