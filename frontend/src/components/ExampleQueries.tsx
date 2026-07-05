"use client";

const EXAMPLES = [
  "How have Pembrolizumab trials grown since 2015?",
  "How are diabetes trials distributed by phase?",
  "Which countries have the most recruiting Alzheimer's trials?",
  "Compare Nivolumab and Pembrolizumab by phase",
  "Show the sponsor–drug relationships in lung cancer trials",
];

interface Props {
  onPick: (query: string) => void;
}

export function ExampleQueries({ onPick }: Props) {
  return (
    <div className="mx-auto flex w-full max-w-3xl flex-wrap gap-2 px-4 pb-3">
      {EXAMPLES.map((q) => (
        <button
          key={q}
          onClick={() => onPick(q)}
          className="rounded-full border border-border bg-panel/70 px-3 py-1.5 text-xs text-neutral-300 transition-colors hover:border-accent hover:text-neutral-100"
        >
          {q}
        </button>
      ))}
    </div>
  );
}
