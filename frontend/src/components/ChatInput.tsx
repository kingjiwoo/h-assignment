"use client";

import { ArrowUp, Loader2 } from "lucide-react";
import { FormEvent, KeyboardEvent, useState } from "react";

interface Props {
  onSubmit: (text: string) => void;
  disabled?: boolean;
  placeholder?: string;
}

export function ChatInput({ onSubmit, disabled, placeholder }: Props) {
  const [value, setValue] = useState("");

  const submit = () => {
    if (!value.trim() || disabled) return;
    onSubmit(value);
    setValue("");
  };

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    submit();
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      submit();
    }
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="mx-auto w-full max-w-3xl rounded-2xl border border-border bg-panel p-3 shadow-lg"
    >
      <div className="flex items-end gap-2">
        <textarea
          value={value}
          onChange={(e) => setValue(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={disabled}
          rows={1}
          placeholder={placeholder ?? "Ask a question about clinical trials..."}
          className="max-h-40 min-h-[40px] flex-1 resize-none bg-transparent px-2 py-2 text-sm text-neutral-100 placeholder-neutral-500 outline-none disabled:opacity-60"
        />
        <button
          type="submit"
          disabled={disabled || !value.trim()}
          className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-accent text-neutral-900 transition-opacity hover:opacity-90 disabled:opacity-40"
          aria-label="Send"
        >
          {disabled ? (
            <Loader2 className="h-4 w-4 animate-spin" />
          ) : (
            <ArrowUp className="h-4 w-4" />
          )}
        </button>
      </div>
      <p className="mt-1 px-1 text-[10px] text-neutral-500">
        Enter = send · Shift+Enter = newline
      </p>
    </form>
  );
}
