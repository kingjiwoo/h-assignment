import type { ResponseMeta } from "@/lib/types";

interface Props {
  meta: ResponseMeta;
}

export function MetaNotes({ meta }: Props) {
  const chips: { label: string; tone?: "warn" }[] = [];
  if (meta.analysis_type) chips.push({ label: meta.analysis_type });
  if (typeof meta.study_count === "number") {
    chips.push({ label: `studies: ${meta.study_count}` });
  }
  if (meta.capped) chips.push({ label: "capped", tone: "warn" });
  if (meta.source) chips.push({ label: meta.source });

  return (
    <div className="mt-3 space-y-2 text-xs text-neutral-400">
      <div className="flex flex-wrap gap-1.5">
        {chips.map((c, i) => (
          <span
            key={i}
            className={`rounded-full border px-2 py-0.5 ${
              c.tone === "warn"
                ? "border-amber-500/40 bg-amber-500/10 text-amber-300"
                : "border-border bg-panel/60 text-neutral-300"
            }`}
          >
            {c.label}
          </span>
        ))}
      </div>
      {meta.notes && meta.notes.length > 0 && (
        <ul className="list-disc space-y-0.5 pl-5 text-[11px] leading-5">
          {meta.notes.map((n, i) => (
            <li key={i}>{n}</li>
          ))}
        </ul>
      )}
    </div>
  );
}
