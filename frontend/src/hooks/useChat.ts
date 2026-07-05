"use client";

import { useCallback, useRef, useState } from "react";

import { ApiError, postQuery } from "@/lib/api";
import type { ChatMessage, QueryRequest } from "@/lib/types";

let counter = 0;
const nextId = () => `${Date.now()}-${counter++}`;

export function useChat() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isSending, setIsSending] = useState(false);
  const abortRef = useRef<AbortController | null>(null);

  const send = useCallback(async (query: string) => {
    const trimmed = query.trim();
    if (!trimmed || isSending) return;

    abortRef.current?.abort();
    const controller = new AbortController();
    abortRef.current = controller;

    const userMsg: ChatMessage = { id: nextId(), role: "user", text: trimmed };
    const pendingId = nextId();
    setMessages((prev) => [
      ...prev,
      userMsg,
      { id: pendingId, role: "assistant", pending: true },
    ]);
    setIsSending(true);

    try {
      const req: QueryRequest = { query: trimmed };
      const response = await postQuery(req, controller.signal);
      setMessages((prev) =>
        prev.map((m) => (m.id === pendingId ? { ...m, pending: false, response } : m)),
      );
    } catch (err) {
      if ((err as Error).name === "AbortError") return;
      const detail =
        err instanceof ApiError
          ? typeof err.detail === "string"
            ? err.detail
            : JSON.stringify(err.detail)
          : (err as Error).message;
      setMessages((prev) =>
        prev.map((m) =>
          m.id === pendingId
            ? {
                ...m,
                role: "error",
                pending: false,
                text: `요청 실패: ${detail}`,
              }
            : m,
        ),
      );
    } finally {
      setIsSending(false);
      abortRef.current = null;
    }
  }, [isSending]);

  const abort = useCallback(() => {
    abortRef.current?.abort();
  }, []);

  const reset = useCallback(() => {
    abortRef.current?.abort();
    abortRef.current = null;
    setMessages([]);
    setIsSending(false);
  }, []);

  return { messages, isSending, send, abort, reset };
}
