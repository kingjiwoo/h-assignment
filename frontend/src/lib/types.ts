export type ChartType =
  | "bar_chart"
  | "grouped_bar_chart"
  | "time_series"
  | "scatter_plot"
  | "histogram"
  | "network_graph"
  | "no_data";

export type AnalysisType =
  | "time_trend"
  | "distribution"
  | "comparison"
  | "geo"
  | "network";

export interface EncodingChannel {
  field: string;
  type?: "temporal" | "quantitative" | "nominal" | "ordinal";
}

export interface NetworkNode {
  id: string;
  kind: string;
  degree: number;
}

export interface NetworkEdge {
  source: string;
  target: string;
  weight: number;
}

export interface NetworkData {
  nodes: NetworkNode[];
  edges: NetworkEdge[];
}

export interface VisualizationSpec {
  type: ChartType;
  title: string;
  encoding: Record<string, unknown>;
  data: Record<string, unknown>[] | NetworkData;
}

export interface ResponseMeta {
  filters: Record<string, unknown>;
  analysis_type: AnalysisType | null;
  source: string;
  study_count: number;
  capped: boolean;
  notes: string[];
}

export interface Citation {
  nct_id: string;
  excerpt: string;
}

export interface QueryResponse {
  visualization: VisualizationSpec;
  meta: ResponseMeta;
  citations: Record<string, Citation[]> | null;
}

export interface QueryRequest {
  query: string;
  drug_name?: string;
  condition?: string;
  sponsor?: string;
  country?: string;
  trial_phase?: string;
  start_year?: number;
  end_year?: number;
}

export type ChatRole = "user" | "assistant" | "error";

export interface ChatMessage {
  id: string;
  role: ChatRole;
  text?: string;
  response?: QueryResponse;
  pending?: boolean;
}
