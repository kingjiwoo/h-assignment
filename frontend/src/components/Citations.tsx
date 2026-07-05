"use client";

import { ChevronDown, ExternalLink } from "lucide-react";
import { useState } from "react";

import type { Citation } from "@/lib/types";

interface Props {
  citations: Record<string, Citation[]>;
}

export function Citations({ citations }: Props) {
  const [open, setOpen] = useState(false);
  const buckets = Object.entries(citations);
  const total = buckets.reduce((n, [, refs]) => n + refs.length, 0);
  if (total === 0) return null;

  return (
    <details
      open={open}
      onToggle={(e) => setOpen((e.target as HTMLDetailsElement).open)}
      className="mt-4 rounded-lg border border-border bg-panel/60"
    >
      <summary className="flex cursor-pointer list-none items-center justify-between gap-2 rounded-lg px-3 py-2 text-xs text-neutral-300 hover:bg-panel">
        <span>Citations · {total} excerpts / {buckets.length} buckets</span>
        <ChevronDown
          className={`h-3.5 w-3.5 transition-transform ${open ? "rotate-180" : ""}`}
        />
      </summary>
      <div className="max-h-72 space-y-3 overflow-y-auto border-t border-border px-3 py-3">
        {buckets.map(([bucket, refs]) => (
          <div key={bucket}>
            <div className="mb-1 text-[11px] font-medium uppercase tracking-wide text-neutral-400">
              {bucket}
            </div>
            <ul className="space-y-1">
              {refs.map((r) => (
                <li key={r.nct_id} className="flex gap-2 text-[12px] text-neutral-300">
                  <a
                    href={`https://clinicaltrials.gov/study/${r.nct_id}`}
                    target="_blank"
                    rel="noreferrer"
                    className="flex shrink-0 items-center gap-0.5 font-mono text-accent hover:underline"
                  >
                    {r.nct_id}
                    <ExternalLink className="h-3 w-3" />
                  </a>
                  <span className="text-neutral-400">— {r.excerpt}</span>
                </li>
              ))}
            </ul>
          </div>
        ))}
      </div>
    </details>
  );
}
