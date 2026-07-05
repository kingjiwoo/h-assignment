# Frontend — ClinicalTrials.gov Query Agent (Chat UI)

백엔드(`app/`)의 `POST /query`를 호출해 시각화 스펙(JSON)을 받아 채팅형 UI로 렌더링하는 Next.js 15 SPA.

- **Stack:** Next.js 15 (App Router) · React 19 · TypeScript · Tailwind CSS
- **Charts:** Vega-Lite (bar / grouped bar / time series) via `react-vega` + `react-force-graph-2d` (network)
- **Renders:** 5개 시각화 타입 (`bar_chart`, `grouped_bar_chart`, `time_series`, `network_graph`, `no_data`) + Citations + Meta notes

## 실행

```bash
# 1) 백엔드 (루트에서)
uv run uvicorn app.main:app --reload           # :8000

# 2) 프론트엔드 (이 폴더에서)
cp .env.local.example .env.local               # 백엔드 URL 커스텀 필요할 때만 수정
pnpm install
pnpm dev                                        # :3000
```

브라우저에서 http://localhost:3000 → 예시 쿼리 칩 클릭 또는 자유 입력.

## 환경변수

| 변수 | 기본값 | 설명 |
|---|---|---|
| `NEXT_PUBLIC_API_BASE` | `http://localhost:8000` | 백엔드 base URL |

백엔드의 CORS는 기본으로 `http://localhost:3000`, `http://127.0.0.1:3000`을 허용합니다. 다른 오리진에서 띄우려면 백엔드 `CORS_ALLOW_ORIGINS` 환경변수를 추가하세요.

## 구조

```
src/
├── app/                       Next.js App Router 페이지
│   ├── layout.tsx
│   ├── page.tsx               채팅 페이지 (유일한 route)
│   └── globals.css
├── components/
│   ├── ChatInput.tsx
│   ├── MessageList.tsx
│   ├── UserMessage.tsx
│   ├── AssistantMessage.tsx   VisualizationCard + Meta + Citations 조립
│   ├── VisualizationCard.tsx  viz.type → 차트 컴포넌트 dispatch
│   ├── MetaNotes.tsx          study_count / capped / notes 표시
│   ├── Citations.tsx          버킷별 접기/펴기 + CT.gov 링크
│   ├── ExampleQueries.tsx     빈 상태에서 예시 5개 프리셋
│   └── charts/
│       ├── VegaChart.tsx        react-vega 얇은 래퍼
│       ├── TimeSeriesChart.tsx
│       ├── BarChart.tsx
│       ├── GroupedBarChart.tsx
│       ├── NetworkGraph.tsx     react-force-graph-2d
│       └── NoDataCard.tsx
├── hooks/
│   └── useChat.ts             messages[] state + send + abort
└── lib/
    ├── types.ts               백엔드 QueryResponse의 TS 미러
    └── api.ts                 postQuery(): 타입드 fetch
```

## 설계 메모

- **채팅 UX + single-turn 백엔드 호환**: 프론트가 자체적으로 messages 배열을 유지하되, 매 요청은 단일 `POST /query`. 백엔드가 향후 `conversation_id`를 지원하면 `lib/api.ts` + `hooks/useChat.ts` 두 파일만 수정.
- **차트 라이브러리 분리 근거**: 백엔드의 `encoding`이 이미 Vega-Lite 스타일(`x.field/type`, `y.field/type`)이라 4개 타입은 Vega-Lite로 얇게 매핑. Network만 힘 기반 시뮬레이션이 필요해 `react-force-graph-2d`를 별도 사용.
- **Network 상세**: `nodes[{id,kind,degree}]`, `edges[{source,target,weight}]` 그대로 사용 (백엔드 스펙). node 크기 = degree, edge 굵기 = weight, 색상 = kind.
- **Citations**: 버킷별로 나눠 접기/펴기, `nct_id` 클릭 → `https://clinicaltrials.gov/study/{nct_id}` 새 탭.
- **Vega SSR**: `react-vega` 컴포넌트는 브라우저 Canvas가 필요해 `"use client"` 컴포넌트에서만 사용. `next.config.mjs`에서 `canvas` 모듈은 브라우저 alias를 `false`로 두어 번들 경고 제거.
