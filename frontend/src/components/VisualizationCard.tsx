"use client";

import type { NetworkData, VisualizationSpec } from "@/lib/types";

import { BarChart } from "./charts/BarChart";
import { GroupedBarChart } from "./charts/GroupedBarChart";
import { NetworkGraph } from "./charts/NetworkGraph";
import { NoDataCard } from "./charts/NoDataCard";
import { TimeSeriesChart } from "./charts/TimeSeriesChart";

interface Props {
  spec: VisualizationSpec;
  notes?: string[];
}

export function VisualizationCard({ spec, notes }: Props) {
  const { type, title, encoding, data } = spec;

  if (type === "no_data") {
    return <NoDataCard title={title} notes={notes} />;
  }

  if (type === "network_graph") {
    return <NetworkGraph title={title} data={data as NetworkData} />;
  }

  const rows = Array.isArray(data) ? (data as Record<string, unknown>[]) : [];

  switch (type) {
    case "time_series":
      return <TimeSeriesChart title={title} encoding={encoding} data={rows} />;
    case "bar_chart":
      return <BarChart title={title} encoding={encoding} data={rows} />;
    case "grouped_bar_chart":
      return <GroupedBarChart title={title} encoding={encoding} data={rows} />;
    default:
      return (
        <NoDataCard
          title={`Unsupported visualization type: ${type}`}
          notes={["The backend returned a new chart type."]}
        />
      );
  }
}
