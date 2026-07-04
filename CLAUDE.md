# ClinicalTrials.gov Query-to-Visualization Agent (Backend) — 과제 컨텍스트

## 과제 요약

**목표:** 자연어 임상시험 질문 → ClinicalTrials.gov API 조회 → 시각화 타입 판단 → 구조화된 시각화 스펙(JSON) 반환하는 백엔드 서비스.
시간 박스: ~24시간. AI 도구/인터넷 사용 자유 (단, README에 사용 내역·검증 방법·직접 구현 vs 생성 구분 명시 필수).

### 입력
- 필수: `query` (string, 자연어)
- 선택(직접 정의): `drug_name`, `condition`, `trial_phase`, `sponsor`, `country`, `start_year`/`end_year` 등
- 요청 스키마 문서화 필수 (필드명/타입/필수여부/검증규칙)

### 출력
- `visualization`: `type`(bar_chart/time_series/scatter/histogram/network_graph 등), `title`, `encoding`(필드→시각채널 매핑), `data`
- `meta`: 단위/정렬/그룹화/가정·필터 노트 등
- 응답 스키마 문서화 필수 — 프론트 엔지니어가 추측 없이 렌더러 구현 가능해야 함

### 시각화 타입 (다양성이 핵심 평가 요소)
bar/grouped bar chart, time series, scatter plot, histogram, **network graph**(drug↔sponsor, drug↔drug 등 엔티티 관계) — 단일 차트 지원보다 여러 타입 + 넓은 질문 커버리지가 고득점.

### 지원 권장 질문 카테고리 (비필수 예시, 그러나 커버리지 평가 기준)
- Time trends: "연도별 [drug] 시험 수 변화?"
- Distributions: "[condition] 시험의 phase별 분포?"
- Comparisons: "Drug A vs Drug B phase 비교"
- Geographic patterns: "[condition] 모집 중인 시험이 많은 국가는?"
- Relationships/networks: "[condition] sponsor↔drug 네트워크", "drug↔drug combination 네트워크"

### 보너스: Deep Citations
각 시각화 데이터 포인트(막대/시간구간/노드·엣지)에 `nct_id` + API 응답에서 가져온 **정확한 텍스트 발췌**를 근거로 첨부. 난이도 높음 — 여유 있으면 구현.

### 제출물
1. 전체 소스코드
2. README: 실행법, 요청/응답 스키마, 설계 결정·트레이드오프, 한계점/개선점, AI 도구 사용 내역
3. 3~5개 예시 쿼리 + 실제 JSON 출력
4. (선택) 간단 UI/배포/데모 영상

### 평가 기준 (가중치)
| 항목 | 비중 | 핵심 체크 |
|---|---|---|
| 시스템 설계 | 35% | 합리적 설계 결정, 유지보수/확장 가능한 구조, 실 API 데이터의 sensible 처리 |
| AI/에이전트 설계 | 20% | 할루시네이션 유발 단계 회피, 검증/제약 존재, 합리적 계획·추론+적절한 도구 사용 |
| 코드 품질 | 20% | 가독성/구조/문서화, 정확성·견고성 |
| 쿼리·시각화 커버리지 | 15% | 질문 유형 폭, one-off hack 없는 다중 클래스 처리, 풍부한 시각화(network graph 등) |
| 입출력 설계 | 10% | 명확/비모호 스키마, 프론트 친화적 스펙 |
| (보너스) Deep citation | 가점 | 소스 추적성 |

---

## ClinicalTrials.gov API 조사 결과 (2026-07-04 실측)

**Base URL:** `https://clinicaltrials.gov/api/v2/` — API 키 불필요, 공개.
현재 버전: `2.0.5` (`GET /version`으로 확인 가능, dataTimestamp 매일 갱신).

### 핵심 엔드포인트
- `GET /studies` — 메인 검색/필터링 엔드포인트.
  - `query.intr` — intervention/drug 이름 검색 (예: `Pembrolizumab`)
  - `query.cond` — condition/disease 검색
  - `query.spons` — sponsor 이름 검색
  - `query.term` — 전문(full-text) 검색
  - `filter.overallStatus` — 예: `RECRUITING`, `COMPLETED` 등
  - `fields` — 반환 필드를 콤마로 선택 지정 가능 (응답 크기 절감에 중요)
  - `pageSize` — 최대 **1000** (실측 확인됨)
  - `pageToken` / 응답의 `nextPageToken` — 커서 기반 페이지네이션 (offset 아님)
  - `sort` — 예: `StartDate` 등 필드 기준 정렬
- `GET /stats/field/values?fields=Phase` — enum 필드의 값별 개수를 **서버가 직접 집계**해서 반환 (예: Phase 분포). 이런 필드는 클라이언트에서 전량 fetch해서 집계할 필요 없이 바로 활용 가능.
- `GET /stats/size` — 전체 study 수(현재 592,210건) 등 통계.
- `GET /studies/metadata` — 전체 필드 스키마 트리(설명/타입/제약 포함). 프롬프트에 필드 후보를 주입할 때 근거 자료로 활용 가능.
- `GET /studies/{nctId}` — 단일 study 상세 (deep citation 발췌용).

### ⚠️ 중요한 설계 제약: 서버사이드 group-by 없음
`time_series`(연도별 추이), phase 분포(Phase 외 필드), network graph(sponsor↔drug, drug↔drug co-occurrence) 등은 **`stats/field/values`가 커버하지 못하는 대부분의 집계**를 백엔드가 직접 study 목록을 받아와 메모리에서 집계해야 함.
→ 설계 시 반드시 고려할 것:
- `fields` 파라미터로 필요한 필드만 받아서 payload 최소화
- `pageSize=1000` + `pageToken` 페이징으로 필요한 만큼만 수집 (전체 59만 건을 다 받으면 안 됨 — 질문의 필터 범위 내에서만)
- 집계에 필요한 study 수의 상한(cap)을 두고 "이 결과는 최근/상위 N건 기준"이라는 걸 `meta.notes`에 명시하는 게 정직한 설계

### 응답 데이터 구조 (실측)
```
protocolSection:
  identificationModule: { nctId, briefTitle, officialTitle }
  statusModule: { overallStatus, startDateStruct{date}, completionDateStruct{date}, ... }
  sponsorCollaboratorsModule: { leadSponsor{name,class}, collaborators[{name}] }  # collaborators는 없을 수도 있음
  conditionsModule: { conditions[] }
  designModule: { phases[] }  # 값: NA, EARLY_PHASE1, PHASE1, PHASE2, PHASE3, PHASE4
  armsInterventionsModule: { interventions[{type, name}] }  # type: DRUG, DEVICE, BEHAVIORAL 등 — drug↔drug network의 재료
  contactsLocationsModule:
    locations[{ facility, status, city, country, geoPoint{lat,lon} }]  # 지리적 시각화 재료
    overallOfficials[{name, affiliation, role}]
    centralContacts[...]
```

### 네트워크 그래프 설계에 바로 쓸 수 있는 필드
- **sponsor↔drug**: `sponsorCollaboratorsModule.leadSponsor.name` × `armsInterventionsModule.interventions[].name` (type=DRUG 필터)
- **drug↔drug (combination 연구)**: 같은 study 안에 `interventions[].type=DRUG`가 2개 이상이면 co-occurrence edge로 집계
- **country 분포**: `contactsLocationsModule.locations[].country` (한 study가 여러 국가를 가질 수 있음 — 카운트 시 study 단위 dedupe 필요)

### Phase 값 참고 (stats/field/values 실측)
`NA`(230,928), `PHASE2`(89,124), `PHASE1`(64,929), `PHASE3`(49,364), `PHASE4`(35,440), `EARLY_PHASE1`(6,368) — missing 140,431건.

---

## 득점 전략 메모

1. **35% 시스템 설계 + 15% 커버리지가 합쳐서 절반**이므로, "질문 해석 → 데이터 조회 → 집계 → 시각화 타입 선택 → 스펙 생성"을 **하나의 일관된 파이프라인**으로 설계하고, 질문 카테고리별 특수 케이스(hack)를 최소화하는 게 핵심. 예: "질문 → (LLM) 구조화된 intent(entity, metric, groupby, chart_hint) 추출 → intent를 API 쿼리로 변환하는 범용 어댑터 → 범용 집계 함수 → 시각화 타입 선택 룰/LLM" 같은 계층화가 유리.
2. **20% AI/에이전트 설계**는 "할루시네이션 회피"가 명시적 기준 → LLM이 숫자(trial_count 등)를 직접 생성하게 하면 안 되고, 반드시 **API에서 가져온 실측 데이터를 코드로 집계**한 후 LLM은 intent 해석·타입 선택·제목 생성 등 "판단"에만 관여시키는 구조가 안전함. 검증/제약(예: 빈 결과 처리, 필드 존재 검증, pydantic 스키마 검증)도 명시적으로 넣을 것.
3. **network graph를 최소 1개는 실제로 동작하게** 만드는 게 배점상 유리 (섹션 4/7에서 반복 강조됨).
4. **Deep citation은 보너스**이지만 구조가 이미 nct_id 단위로 데이터를 다루므로, 각 집계 결과에 기여한 study들의 `nctId`+발췌 필드를 함께 들고 다니는 설계를 처음부터 하면 나중에 추가 비용이 적음.
5. README에 AI 도구 사용/검증 방법을 반드시 기록 — 평가 항목에 명시적으로 들어있음.
