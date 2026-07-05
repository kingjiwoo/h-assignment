"use client";

import { Loader2 } from "lucide-react";

import type { ChatMessage } from "@/lib/types";

import { Citations } from "./Citations";
import { MetaNotes } from "./MetaNotes";
import { VisualizationCard } from "./VisualizationCard";

interface Props {
  message: ChatMessage;
}

export function AssistantMessage({ message }: Props) {
  if (message.pending) {
    return (
      <div className="flex items-center gap-2 rounded-2xl border border-border bg-panel px-4 py-3 text-sm text-neutral-400">
        <Loader2 className="h-4 w-4 animate-spin text-accent" />
        ClinicalTrials.gov 조회 및 집계 중…
      </div>
    );
  }

  if (message.role === "error") {
    return (
      <div className="rounded-2xl border border-red-500/40 bg-red-500/10 px-4 py-3 text-sm text-red-300">
        {message.text ?? "에러가 발생했습니다."}
      </div>
    );
  }

  const res = message.response;
  if (!res) return null;

  return (
    <div className="rounded-2xl border border-border bg-panel px-4 py-4 shadow-sm">
      <VisualizationCard spec={res.visualization} notes={res.meta.notes} />
      <MetaNotes meta={res.meta} />
      {res.citations && Object.keys(res.citations).length > 0 && (
        <Citations citations={res.citations} />
      )}
    </div>
  );
}
