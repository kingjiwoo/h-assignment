"use client";

import { Sparkles } from "lucide-react";

const EXAMPLES = [
  {
    label: "연도별 추이",
    query: "Show yearly trends of pembrolizumab trials from 2015 to 2023",
  },
  {
    label: "Phase 분포",
    query: "How are diabetes trials distributed across phases?",
  },
  {
    label: "국가 분포",
    query: "Which countries have the most recruiting Alzheimer trials?",
  },
  {
    label: "약물 비교",
    query: "Compare Nivolumab vs Pembrolizumab trials by phase",
  },
  {
    label: "관계망",
    query: "Show sponsor-drug network for lung cancer trials",
  },
];

interface Props {
  onPick: (query: string) => void;
}

export function ExampleQueries({ onPick }: Props) {
  return (
    <div className="mx-auto flex w-full max-w-3xl flex-col items-center gap-4 px-4 py-16 text-center">
      <div className="flex items-center gap-2 text-sm text-neutral-400">
        <Sparkles className="h-4 w-4 text-accent" />
        무엇을 알아볼까요?
      </div>
      <h1 className="text-2xl font-semibold text-neutral-100">
        ClinicalTrials.gov Query Agent
      </h1>
      <p className="max-w-lg text-sm text-neutral-400">
        자연어로 질문하면 실제 ClinicalTrials.gov API를 조회해 시각화를 만들어 드립니다.
        아래 예시로 시작해 보세요.
      </p>
      <div className="mt-4 flex flex-wrap justify-center gap-2">
        {EXAMPLES.map((ex) => (
          <button
            key={ex.query}
            onClick={() => onPick(ex.query)}
            className="rounded-full border border-border bg-panel px-3 py-1.5 text-xs text-neutral-300 transition-colors hover:border-accent hover:text-neutral-100"
          >
            {ex.label}
          </button>
        ))}
      </div>
    </div>
  );
}
