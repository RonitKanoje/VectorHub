import { ArrowUp, BarChart2, FileText, Mic, MicOff, X } from "lucide-react";
import { useState, useRef } from "react";
import PlusButton from "./PlusButton";
import api from "../services/api";

export interface MediaPayload {
  media: "youtube" | "audio" | "video" | "text" | "document" | "dataset";
  path?: string;
  language?: string | null;
  file?: File;
}

export interface UploadedItem {
  type: string;
  name: string;
  icon?: string;
}

interface MessageInputProps {
  disabled?: boolean;
  isSending?: boolean;
  isAnalystMode?: boolean;
  uploadedItems?: UploadedItem[];
  onSend: (content: string) => Promise<void>;
  onProcessMedia: (payload: MediaPayload) => Promise<void>;
  onRemoveUpload?: (index: number) => void;
}

const MEDIA_ICONS: Record<string, string> = {
  youtube: "📺",
  audio: "🎵",
  video: "🎥",
  document: "📄",
  text: "📝",
  dataset: "📊",
};

const MessageInput = ({
  disabled = false,
  isSending = false,
  isAnalystMode = false,
  uploadedItems = [],
  onSend,
  onProcessMedia,
  onRemoveUpload,
}: MessageInputProps) => {
  const [value, setValue] = useState("");
  const [isRecording, setIsRecording] = useState(false);
  const [isTranscribing, setIsTranscribing] = useState(false);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      audioChunksRef.current = [];

      const mediaRecorder = new MediaRecorder(stream, { mimeType: "audio/webm" });
      mediaRecorderRef.current = mediaRecorder;

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = async () => {
        setIsTranscribing(true);
        try {
          const audioBlob = new Blob(audioChunksRef.current, { type: "audio/webm" });
          const formData = new FormData();
          formData.append("audio", audioBlob, "recording.webm");

          const response = await api.post<{ text: string }>("/api/ai/transcribe", formData, {
            headers: { "Content-Type": "multipart/form-data" },
          });

          if (response.data.text) {
            setValue((prev) => (prev + " " + response.data.text).trim());
          }
        } catch (err) {
          console.error("Transcription failed", err);
        } finally {
          setIsTranscribing(false);
        }
        // Clean up stream tracks
        stream.getTracks().forEach((t) => t.stop());
      };

      mediaRecorder.start();
      setIsRecording(true);
    } catch (err) {
      console.error("Microphone access error", err);
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== "inactive") {
      mediaRecorderRef.current.stop();
    }
    setIsRecording(false);
  };

  const handleSubmit = async () => {
    const content = value.trim();
    if (!content || disabled || isSending) return;
    setValue("");
    await onSend(content);
  };

  return (
    <div className="shrink-0 border-t border-slate-200 dark:border-slate-800 bg-white/90 dark:bg-slate-900/90 p-3 pb-[max(0.75rem,env(safe-area-inset-bottom))] backdrop-blur sm:p-4">
      {/* Upload pills */}
      {uploadedItems.length > 0 && (
        <div className="mx-auto mb-2 flex max-w-4xl flex-wrap gap-1.5">
          {uploadedItems.map((item, i) => (
            <div
              key={i}
              className="flex items-center gap-1.5 rounded-full border border-slate-200 dark:border-slate-700 bg-slate-100 dark:bg-slate-800 px-2.5 py-1 text-xs text-slate-700 dark:text-slate-300"
            >
              <span>{MEDIA_ICONS[item.type] ?? "📎"}</span>
              <span className="max-w-[120px] truncate">{item.name}</span>
              {onRemoveUpload && (
                <button
                  onClick={() => onRemoveUpload(i)}
                  className="text-slate-400 hover:text-red-500 transition"
                >
                  <X className="h-3 w-3" />
                </button>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Analyst mode banner */}
      {isAnalystMode && (
        <div className="mx-auto mb-2 flex max-w-4xl items-center gap-2 rounded-xl bg-violet-50 dark:bg-violet-950/40 border border-violet-200 dark:border-violet-800 px-3 py-1.5 text-xs text-violet-700 dark:text-violet-300">
          <BarChart2 className="h-3.5 w-3.5" />
          <span>Analyst Mode active — upload a CSV/Excel dataset to query it</span>
        </div>
      )}

      <div className="relative mx-auto w-full max-w-4xl">
        <input
          type="text"
          value={isTranscribing ? "Transcribing..." : value}
          placeholder={
            disabled
              ? "Loading conversation..."
              : isAnalystMode
              ? "Ask a question about your dataset..."
              : "Ask anything, or upload content for RAG..."
          }
          disabled={disabled || isSending || isTranscribing}
          className="h-14 w-full rounded-2xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 py-3 pl-14 pr-28 text-sm text-slate-950 dark:text-white shadow-sm outline-none transition focus:border-cyan-500 dark:focus:border-cyan-500 focus:bg-white dark:focus:bg-slate-700 focus:ring-2 focus:ring-cyan-500/20 disabled:cursor-not-allowed disabled:bg-slate-100 dark:disabled:bg-slate-900 disabled:text-slate-400"
          onChange={(e) => setValue(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter") {
              e.preventDefault();
              void handleSubmit();
            }
          }}
        />
        <PlusButton disabled={isSending} onProcessMedia={onProcessMedia} />
        <button
          type="button"
          onClick={isRecording ? stopRecording : startRecording}
          disabled={disabled || isSending || isTranscribing}
          className={`absolute right-14 top-1/2 flex h-9 w-9 -translate-y-1/2 items-center justify-center rounded-xl transition ${
            isRecording
              ? "bg-red-500 text-white animate-pulse"
              : isTranscribing
              ? "bg-amber-500 text-white animate-pulse"
              : "bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-600"
          }`}
          aria-label={isRecording ? "Stop recording" : "Start recording"}
        >
          {isRecording ? <MicOff className="h-4 w-4" /> : <Mic className="h-4 w-4" />}
        </button>
        <button
          type="button"
          disabled={!value.trim() || disabled || isSending}
          onClick={() => void handleSubmit()}
          className="absolute right-3 top-1/2 flex h-9 w-9 -translate-y-1/2 items-center justify-center rounded-xl bg-slate-950 dark:bg-cyan-600 text-white transition hover:bg-cyan-700 disabled:cursor-not-allowed disabled:bg-slate-300 dark:disabled:bg-slate-700"
          aria-label="Send message"
        >
          <ArrowUp className="h-4 w-4" />
        </button>
      </div>
    </div>
  );
};

export default MessageInput;
