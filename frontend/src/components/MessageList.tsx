"use client";

import { useEffect, useRef } from "react";

import type { ChatMessage } from "@/lib/types";

import { AssistantMessage } from "./AssistantMessage";
import { UserMessage } from "./UserMessage";

interface Props {
  messages: ChatMessage[];
}

export function MessageList({ messages }: Props) {
  const endRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [messages]);

  return (
    <div className="mx-auto w-full max-w-3xl space-y-4 px-4 py-6">
      {messages.map((m) => (
        <div key={m.id}>
          {m.role === "user" ? (
            <UserMessage text={m.text ?? ""} />
          ) : (
            <AssistantMessage message={m} />
          )}
        </div>
      ))}
      <div ref={endRef} />
    </div>
  );
}
