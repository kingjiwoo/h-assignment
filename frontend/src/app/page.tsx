"use client";

import { ChatInput } from "@/components/ChatInput";
import { ExampleQueries } from "@/components/ExampleQueries";
import { MessageList } from "@/components/MessageList";
import { useChat } from "@/hooks/useChat";

export default function ChatPage() {
  const { messages, isSending, send, reset } = useChat();
  const empty = messages.length === 0;

  return (
    <main className="flex min-h-screen flex-col">
      <header className="border-b border-border bg-panel/60 backdrop-blur">
        <div className="mx-auto flex w-full max-w-3xl items-center justify-between px-4 py-3">
          <button
            type="button"
            onClick={reset}
            disabled={empty}
            title="새 대화 시작"
            className="text-sm font-medium text-neutral-100 transition hover:text-white disabled:cursor-default disabled:text-neutral-100 disabled:hover:text-neutral-100"
          >
            ClinicalTrials.gov Query Agent
          </button>
          <div className="flex items-center gap-3">
            {!empty && (
              <button
                type="button"
                onClick={reset}
                className="rounded-md border border-border px-2 py-1 text-[11px] text-neutral-300 transition hover:border-neutral-500 hover:text-neutral-100"
              >
                새 대화
              </button>
            )}
            <a
              href="https://clinicaltrials.gov/data-api/api"
              target="_blank"
              rel="noreferrer"
              className="text-[11px] text-neutral-500 hover:text-neutral-300"
            >
              CT.gov v2 API
            </a>
          </div>
        </div>
      </header>

      <div className="flex-1 overflow-y-auto">
        <MessageList messages={messages} />
      </div>

      <div className="sticky bottom-0 border-t border-border bg-surface/95 px-4 py-3 backdrop-blur">
        {empty && <ExampleQueries onPick={send} />}
        <ChatInput onSubmit={send} disabled={isSending} />
      </div>
    </main>
  );
}
