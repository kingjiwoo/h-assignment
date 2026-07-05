"use client";

import { useEffect, useRef } from "react";
import { useVegaEmbed } from "react-vega";
import type { VisualizationSpec } from "vega-embed";

interface Props {
  spec: VisualizationSpec;
  height?: number;
}

export function VegaChart({ spec, height = 300 }: Props) {
  const containerRef = useRef<HTMLDivElement>(null);
  const result = useVegaEmbed({
    ref: containerRef,
    spec,
    options: {
      mode: "vega-lite",
      actions: false,
      renderer: "canvas",
      config: undefined,
    },
  });

  useEffect(() => {
    if (!result || !containerRef.current) return;
    const observer = new ResizeObserver(() => {
      result.view?.resize?.().runAsync?.();
    });
    observer.observe(containerRef.current);
    return () => observer.disconnect();
  }, [result]);

  return <div ref={containerRef} className="w-full" style={{ minHeight: height }} />;
}
