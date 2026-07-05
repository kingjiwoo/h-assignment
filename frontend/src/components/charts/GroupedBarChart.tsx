"use client";

import type { VisualizationSpec } from "vega-embed";

import { VegaChart } from "./VegaChart";
import { fieldOf, vegaDarkConfig } from "./vegaShared";

interface Props {
  title: string;
  encoding: Record<string, unknown>;
  data: Record<string, unknown>[];
}

export function GroupedBarChart({ title, encoding, data }: Props) {
  const xField = fieldOf(encoding, "x", "category");
  const series = (encoding?.series as string[]) ?? inferSeries(data, xField);

  const spec = {
    $schema: "https://vega.github.io/schema/vega-lite/v5.json",
    title,
    width: "container",
    height: 320,
    autosize: { type: "fit", contains: "padding" },
    data: { values: data },
    transform: [
      { fold: series, as: ["group", "trial_count"] },
    ],
    mark: { type: "bar", cornerRadiusEnd: 3 },
    encoding: {
      x: {
        field: xField,
        type: "nominal",
        title: xField,
        axis: { labelAngle: -30 },
      },
      xOffset: { field: "group", type: "nominal" },
      y: { field: "trial_count", type: "quantitative", title: "Trials" },
      color: { field: "group", type: "nominal", title: "Group" },
      tooltip: [
        { field: xField, type: "nominal" },
        { field: "group", type: "nominal" },
        { field: "trial_count", type: "quantitative" },
      ],
    },
    config: vegaDarkConfig,
  } satisfies Record<string, unknown>;

  return (
    <div className="w-full">
      <VegaChart spec={spec as unknown as VisualizationSpec} height={320} />
    </div>
  );
}

function inferSeries(data: Record<string, unknown>[], xField: string): string[] {
  if (!data?.length) return [];
  return Object.keys(data[0]).filter((k) => k !== xField);
}
