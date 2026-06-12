import { ArrowUp } from "lucide-react";
import { useState } from "react";
import PlusButton from "./PlusButton";

export interface MediaPayload {
  media: "youtube" | "audio" | "video" | "text";
  path?: string;
  language?: string | null;
  file?: {
    name: string;
    contentBase64: string;
  };
}

interface MessageInputProps {
  disabled?: boolean;
  isSending?: boolean;
  onSend: (content: string) => Promise<void>;
  onProcessMedia: (payload: MediaPayload) => Promise<void>;
}

const MessageInput = ({
  disabled = false,
  isSending = false,
  onSend,
  onProcessMedia,
}: MessageInputProps) => {
  const [value, setValue] = useState("");

  const handleSubmit = async () => {
    const content = value.trim();
    if (!content || disabled || isSending) return;

    setValue("");
    await onSend(content);
  };

  return (
    <div className="shrink-0 border-t border-slate-200/80 bg-white/90 p-3 pb-[max(0.75rem,env(safe-area-inset-bottom))] backdrop-blur sm:p-4">
      <div className="relative mx-auto w-full max-w-4xl">
        <input
          type="text"
          value={value}
          placeholder={disabled ? "Loading conversation..." : "Ask anything, or upload content for RAG..."}
          disabled={disabled || isSending}
          className="h-14 w-full rounded-2xl border border-slate-200 bg-slate-50 py-3 pl-14 pr-14 text-sm text-slate-950 shadow-sm outline-none transition focus:border-cyan-500 focus:bg-white focus:ring-2 focus:ring-cyan-500/20 disabled:cursor-not-allowed disabled:bg-slate-100 disabled:text-slate-400"
          onChange={(e) => setValue(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter") {
              e.preventDefault();
              void handleSubmit();
            }
          }}
        />
        <PlusButton
          disabled={isSending}
          onProcessMedia={onProcessMedia}
        />
        <button
          type="button"
          disabled={!value.trim() || disabled || isSending}
          onClick={() => void handleSubmit()}
          className="absolute right-3 top-1/2 flex h-9 w-9 -translate-y-1/2 items-center justify-center rounded-xl bg-slate-950 text-white transition hover:bg-cyan-700 disabled:cursor-not-allowed disabled:bg-slate-300"
          aria-label="Send message"
        >
          <ArrowUp className="h-4 w-4" />
        </button>
      </div>
    </div>
  );
};

export default MessageInput;
