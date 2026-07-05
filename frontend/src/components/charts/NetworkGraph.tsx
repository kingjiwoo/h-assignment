"use client";

import dynamic from "next/dynamic";
import { useEffect, useMemo, useRef, useState } from "react";

import type { NetworkData } from "@/lib/types";

const ForceGraph2D = dynamic(() => import("react-force-graph-2d"), {
  ssr: false,
});

interface Props {
  title: string;
  data: NetworkData;
}

const KIND_COLORS: Record<string, string> = {
  sponsor: "#f472b6",
  drug: "#60a5fa",
  intervention: "#60a5fa",
  drug_a: "#a78bfa",
  drug_b: "#34d399",
};

function colorForKind(kind: string): string {
  return KIND_COLORS[kind] ?? "#c8ccd1";
}

export function NetworkGraph({ title, data }: Props) {
  const wrapRef = useRef<HTMLDivElement>(null);
  const [size, setSize] = useState({ width: 600, height: 480 });

  useEffect(() => {
    const el = wrapRef.current;
    if (!el) return;
    const update = () => {
      const rect = el.getBoundingClientRect();
      setSize({
        width: Math.max(320, Math.floor(rect.width)),
        height: 480,
      });
    };
    update();
    const ro = new ResizeObserver(update);
    ro.observe(el);
    return () => ro.disconnect();
  }, []);

  const graphData = useMemo(() => {
    const nodes = (data.nodes ?? []).map((n) => ({
      id: n.id,
      kind: n.kind,
      degree: n.degree,
      val: Math.max(2, n.degree),
    }));
    const links = (data.edges ?? []).map((e) => ({
      source: e.source,
      target: e.target,
      weight: e.weight,
    }));
    return { nodes, links };
  }, [data]);

  const maxDegree = useMemo(
    () => Math.max(1, ...graphData.nodes.map((n) => n.degree)),
    [graphData.nodes],
  );

  return (
    <div className="w-full">
      <div className="mb-2 text-sm font-medium text-neutral-100">{title}</div>
      <div
        ref={wrapRef}
        className="w-full rounded-lg border border-border bg-[#0f1216]"
        style={{ height: 480 }}
      >
        <ForceGraph2D
          width={size.width}
          height={size.height}
          graphData={graphData}
          backgroundColor="#0f1216"
          nodeRelSize={4}
          linkColor={() => "rgba(200,204,209,0.3)"}
          linkWidth={(l) => 0.5 + (l as { weight?: number }).weight! * 0.15}
          nodeCanvasObject={(node, ctx, globalScale) => {
            const n = node as { id: string; kind: string; degree: number; x?: number; y?: number };
            const r = 3 + 6 * (n.degree / maxDegree);
            ctx.beginPath();
            ctx.arc(n.x!, n.y!, r, 0, 2 * Math.PI, false);
            ctx.fillStyle = colorForKind(n.kind);
            ctx.fill();
            if (globalScale > 1.2 || n.degree >= maxDegree * 0.5) {
              const label = n.id.length > 24 ? n.id.slice(0, 22) + "…" : n.id;
              ctx.font = `${Math.max(10, 11 / globalScale)}px -apple-system, sans-serif`;
              ctx.fillStyle = "#e6e8eb";
              ctx.textAlign = "left";
              ctx.textBaseline = "middle";
              ctx.fillText(label, n.x! + r + 2, n.y!);
            }
          }}
          nodePointerAreaPaint={(node, color, ctx) => {
            const n = node as { degree: number; x?: number; y?: number };
            const r = 3 + 6 * (n.degree / maxDegree);
            ctx.fillStyle = color;
            ctx.beginPath();
            ctx.arc(n.x!, n.y!, r, 0, 2 * Math.PI, false);
            ctx.fill();
          }}
          cooldownTicks={60}
          d3AlphaDecay={0.04}
        />
      </div>
      <div className="mt-2 flex flex-wrap gap-3 text-xs text-neutral-400">
        {Array.from(new Set(graphData.nodes.map((n) => n.kind))).map((kind) => (
          <span key={kind} className="flex items-center gap-1.5">
            <span
              className="inline-block h-2 w-2 rounded-full"
              style={{ backgroundColor: colorForKind(kind) }}
            />
            {kind}
          </span>
        ))}
        <span>· {graphData.nodes.length} nodes / {graphData.links.length} edges</span>
      </div>
    </div>
  );
}
