import { ArrowUp, Mic, MicOff } from "lucide-react";
import AnalystPlusButton from "./AnalystPlusButton";
import type { MediaPayload } from "../types";

interface AnalystChatInputProps {
  value: string;
  onChange: (value: string) => void;
  onSend: () => void;
  isSending: boolean;
  isRecording: boolean;
  isTranscribing: boolean;
  onToggleRecording: () => void;
  onProcessMedia: (payload: MediaPayload) => void;
}

const AnalystChatInput = ({
  value,
  onChange,
  onSend,
  isSending,
  isRecording,
  isTranscribing,
  onToggleRecording,
  onProcessMedia,
}: AnalystChatInputProps) => {
  return (
    <div className="shrink-0 border-t border-slate-800 bg-slate-900/90 p-3 pb-[max(0.75rem,env(safe-area-inset-bottom))] backdrop-blur sm:p-4">
      <div className="relative mx-auto w-full max-w-4xl">
        <input
          type="text"
          value={isTranscribing ? "Transcribing…" : value}
          placeholder={isSending ? "Analysing your data…" : "Ask a question about your dataset…"}
          disabled={isSending || isTranscribing}
          className="h-14 w-full rounded-2xl border border-slate-700 bg-slate-800 py-3 pl-14 pr-28 text-sm text-white shadow-sm outline-none transition focus:border-violet-500 focus:ring-2 focus:ring-violet-500/20 disabled:cursor-not-allowed disabled:opacity-50"
          onChange={(e) => onChange(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              onSend();
            }
          }}
        />

        <AnalystPlusButton disabled={isSending} onProcessMedia={onProcessMedia} />

        <button
          type="button"
          onClick={onToggleRecording}
          disabled={isSending || isTranscribing}
          className={`absolute right-14 top-1/2 -translate-y-1/2 flex h-9 w-9 items-center justify-center rounded-xl transition ${
            isRecording
              ? "bg-red-500 text-white animate-pulse"
              : isTranscribing
                ? "bg-amber-500 text-white animate-pulse"
                : "bg-slate-700 text-slate-300 hover:bg-slate-600"
          }`}
        >
          {isRecording ? <MicOff className="h-4 w-4" /> : <Mic className="h-4 w-4" />}
        </button>

        <button
          type="button"
          disabled={!value.trim() || isSending}
          onClick={onSend}
          className="absolute right-3 top-1/2 -translate-y-1/2 flex h-9 w-9 items-center justify-center rounded-xl bg-violet-600 text-white transition hover:bg-violet-500 disabled:cursor-not-allowed disabled:bg-slate-700"
        >
          <ArrowUp className="h-4 w-4" />
        </button>
      </div>
    </div>
  );
};

export default AnalystChatInput;