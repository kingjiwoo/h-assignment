import { Info } from "lucide-react";

interface Props {
  title: string;
  notes?: string[];
}

export function NoDataCard({ title, notes }: Props) {
  return (
    <div className="flex flex-col items-start gap-2 rounded-lg border border-border bg-[#0f1216] px-4 py-6 text-sm text-neutral-300">
      <div className="flex items-center gap-2 text-neutral-100">
        <Info className="h-4 w-4 text-accent" />
        {title}
      </div>
      {notes && notes.length > 0 && (
        <ul className="ml-6 list-disc space-y-1 text-xs text-neutral-400">
          {notes.map((n, i) => (
            <li key={i}>{n}</li>
          ))}
        </ul>
      )}
    </div>
  );
}
