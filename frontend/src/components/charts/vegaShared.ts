import type { VisualizationSpec } from "vega-embed";

export const vegaDarkConfig: Record<string, unknown> = {
  background: "transparent",
  view: { stroke: "transparent" },
  axis: {
    domainColor: "#3a4048",
    gridColor: "#2a2f36",
    tickColor: "#3a4048",
    labelColor: "#c8ccd1",
    titleColor: "#e6e8eb",
    labelFontSize: 11,
    titleFontSize: 12,
  },
  legend: {
    labelColor: "#c8ccd1",
    titleColor: "#e6e8eb",
  },
  title: {
    color: "#e6e8eb",
    fontSize: 13,
    fontWeight: 500,
  },
  range: {
    category: [
      "#60a5fa",
      "#f472b6",
      "#34d399",
      "#fbbf24",
      "#a78bfa",
      "#f87171",
      "#22d3ee",
      "#a3e635",
    ],
  },
};

interface EncodingField {
  field?: string;
  type?: string;
}

export function fieldOf(
  encoding: Record<string, unknown>,
  channel: string,
  fallback: string,
): string {
  const c = encoding?.[channel] as EncodingField | undefined;
  return (c && typeof c === "object" && c.field) || fallback;
}

export type VegaSpec = VisualizationSpec;
