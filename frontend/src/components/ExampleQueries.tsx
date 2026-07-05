"use client";

const EXAMPLES = [
  "Pembrolizumab 시험이 2015년부터 어떻게 늘어났나요?",
  "당뇨병 시험은 Phase별로 어떻게 분포돼 있나요?",
  "Alzheimer 임상시험을 모집 중인 나라는 어디가 많나요?",
  "Nivolumab이랑 Pembrolizumab, Phase별로 비교해 주세요",
  "폐암 시험의 스폰서와 약물 관계를 보여주세요",
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
