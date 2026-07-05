"use client";

import type { VisualizationSpec } from "vega-embed";

import { VegaChart } from "./VegaChart";
import { fieldOf, vegaDarkConfig } from "./vegaShared";

interface Props {
  title: string;
  encoding: Record<string, unknown>;
  data: Record<string, unknown>[];
}

export function TimeSeriesChart({ title, encoding, data }: Props) {
  const xField = fieldOf(encoding, "x", "year");
  const yField = fieldOf(encoding, "y", "trial_count");

  const spec = {
    $schema: "https://vega.github.io/schema/vega-lite/v5.json",
    title,
    width: "container",
    height: 260,
    autosize: { type: "fit", contains: "padding" },
    data: { values: data },
    layer: [
      {
        mark: { type: "line", color: "#60a5fa", strokeWidth: 2 },
        encoding: {
          x: { field: xField, type: "ordinal", title: "Year" },
          y: { field: yField, type: "quantitative", title: "Trials" },
        },
      },
      {
        mark: { type: "point", color: "#60a5fa", filled: true, size: 60 },
        encoding: {
          x: { field: xField, type: "ordinal" },
          y: { field: yField, type: "quantitative" },
          tooltip: [
            { field: xField, type: "ordinal", title: "Year" },
            { field: yField, type: "quantitative", title: "Trials" },
          ],
        },
      },
    ],
    config: vegaDarkConfig,
  } satisfies Record<string, unknown>;

  return (
    <div className="w-full">
      <VegaChart spec={spec as unknown as VisualizationSpec} height={260} />
    </div>
  );
}
