# Frontend — ClinicalTrials.gov Query Agent (Chat UI)

Next.js 15 SPA that calls the backend (`app/`) `POST /query`, receives the visualization spec (JSON), and renders it as a chat-style UI.

- **Stack:** Next.js 15 (App Router) · React 19 · TypeScript · Tailwind CSS
- **Charts:** Vega-Lite (bar / grouped bar / time series) via `react-vega` + `react-force-graph-2d` (network)
- **Renders:** 5 visualization types (`bar_chart`, `grouped_bar_chart`, `time_series`, `network_graph`, `no_data`) plus Citations and Meta notes

## Running

```bash
# 1) Backend (from the repo root)
uv run uvicorn app.main:app --reload           # :8000

# 2) Frontend (from this folder)
cp .env.local.example .env.local               # Only edit if you need a custom backend URL
pnpm install
pnpm dev                                        # :3000
```

Open http://localhost:3000 in your browser → click an example query chip or type your own.

## Environment variables

| Variable | Default | Description |
|---|---|---|
| `NEXT_PUBLIC_API_BASE` | `http://localhost:8000` | Backend base URL |

The backend's CORS allows `http://localhost:3000` and `http://127.0.0.1:3000` by default. To host from another origin, add the `CORS_ALLOW_ORIGINS` env var on the backend.

## Layout

```
src/
├── app/                       Next.js App Router pages
│   ├── layout.tsx
│   ├── page.tsx               Chat page (the only route)
│   └── globals.css
├── components/
│   ├── ChatInput.tsx
│   ├── MessageList.tsx
│   ├── UserMessage.tsx
│   ├── AssistantMessage.tsx   Assembles VisualizationCard + Meta + Citations
│   ├── VisualizationCard.tsx  Dispatches on viz.type → the matching chart component
│   ├── MetaNotes.tsx          Displays study_count / capped / notes
│   ├── Citations.tsx          Collapsible per-bucket list + CT.gov links
│   ├── ExampleQueries.tsx     5 preset prompts shown on the empty state
│   └── charts/
│       ├── VegaChart.tsx        Thin wrapper around react-vega
│       ├── TimeSeriesChart.tsx
│       ├── BarChart.tsx
│       ├── GroupedBarChart.tsx
│       ├── NetworkGraph.tsx     react-force-graph-2d
│       └── NoDataCard.tsx
├── hooks/
│   └── useChat.ts             messages[] state + send + abort
└── lib/
    ├── types.ts               TS mirror of the backend QueryResponse
    └── api.ts                 postQuery(): typed fetch
```

## Design notes

- **Chat UX on top of a single-turn backend:** the frontend keeps its own `messages` array, but each request is one `POST /query`. If the backend later adds `conversation_id` support, only `lib/api.ts` and `hooks/useChat.ts` need to change.
- **Why two chart libraries:** the backend's `encoding` is already Vega-Lite-shaped (`x.field/type`, `y.field/type`), so four of the five types map to Vega-Lite thinly. Only the network type needs a force simulation, hence `react-force-graph-2d`.
- **Network details:** we use `nodes[{id,kind,degree}]` and `edges[{source,target,weight}]` verbatim from the backend spec. Node size = degree, edge width = weight, color = kind.
- **Citations:** grouped by bucket with expand/collapse; clicking a `nct_id` opens `https://clinicaltrials.gov/study/{nct_id}` in a new tab.
- **Vega SSR:** `react-vega` needs the browser canvas, so it is only used inside `"use client"` components. In `next.config.mjs` the `canvas` module is aliased to `false` for the browser bundle, silencing the bundle warning.
