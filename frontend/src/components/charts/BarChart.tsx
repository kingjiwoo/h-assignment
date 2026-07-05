"use client";

import type { VisualizationSpec } from "vega-embed";

import { VegaChart } from "./VegaChart";
import { fieldOf, vegaDarkConfig } from "./vegaShared";

interface Props {
  title: string;
  encoding: Record<string, unknown>;
  data: Record<string, unknown>[];
}

export function BarChart({ title, encoding, data }: Props) {
  const xField = fieldOf(encoding, "x", "category");
  const yField = fieldOf(encoding, "y", "trial_count");

  const spec = {
    $schema: "https://vega.github.io/schema/vega-lite/v5.json",
    title,
    width: "container",
    height: 300,
    autosize: { type: "fit", contains: "padding" },
    data: { values: data },
    mark: { type: "bar", color: "#60a5fa", cornerRadiusEnd: 3 },
    encoding: {
      x: {
        field: xField,
        type: "nominal",
        sort: "-y",
        title: xField,
        axis: { labelAngle: -30 },
      },
      y: { field: yField, type: "quantitative", title: "Trials" },
      tooltip: [
        { field: xField, type: "nominal" },
        { field: yField, type: "quantitative", title: "Trials" },
      ],
    },
    config: vegaDarkConfig,
  } satisfies Record<string, unknown>;

  return (
    <div className="w-full">
      <VegaChart spec={spec as unknown as VisualizationSpec} height={300} />
    </div>
  );
}
