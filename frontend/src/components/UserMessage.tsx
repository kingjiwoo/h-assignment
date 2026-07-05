interface Props {
  text: string;
}

export function UserMessage({ text }: Props) {
  return (
    <div className="flex justify-end">
      <div className="max-w-[80%] rounded-2xl rounded-br-sm bg-accent/90 px-4 py-2 text-sm text-neutral-900 shadow">
        {text}
      </div>
    </div>
  );
}
