import { ArrowUp, Mic, MicOff } from "lucide-react";
import { useEffect, useRef, useState } from "react";
import PlusButton from "./PlusButton";
import type { MediaPayload } from "../types";
import { WEBSOCKET_BASE_URL } from "../config/env";

interface MessageInputProps {
  disabled?: boolean;
  isSending?: boolean;
  isAnalystMode?: boolean;
  embedded?: boolean;
  onSend: (content: string) => Promise<void>;
  onProcessMedia: (payload: MediaPayload) => Promise<void>;
  onRemoveUpload?: (index: number) => void;
}

const SEGMENT_DURATION_MS = 3000;

const MessageInput = ({
  disabled = false,
  isSending = false,
  isAnalystMode = false,
  embedded = false,
  onSend,
  onProcessMedia,
}: MessageInputProps) => {
  const [value, setValue] = useState("");
  const [isRecording, setIsRecording] = useState(false);
  const [isTranscribing, setIsTranscribing] = useState(false);

  const streamRef = useRef<MediaStream | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const isRecordingRef = useRef(false);
  const segmentTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  // Records exactly one independent, self-contained 3s WebM segment, sends it,
  // then immediately starts the next one. Each MediaRecorder instance is used
  // for a single start()->stop() cycle so every Blob is a fully valid,
  // independently-decodable WebM file. No shared header, no chunk merging.
  const recordSegment = () => {
    const stream = streamRef.current;
    if (!isRecordingRef.current || !stream) return;

    const recorder = new MediaRecorder(stream, { mimeType: "audio/webm" });
    mediaRecorderRef.current = recorder;
    const chunks: BlobPart[] = [];

    recorder.ondataavailable = (event) => {
      if (event.data.size > 0) chunks.push(event.data);
    };

    recorder.onstop = () => {
      const blob = new Blob(chunks, { type: "audio/webm" });
      const ws = wsRef.current;
      if (blob.size > 0 && ws && ws.readyState === WebSocket.OPEN) {
        ws.send(blob);
      }

      if (isRecordingRef.current) {
        recordSegment();
      } else {
        finishStop();
      }
    };

    recorder.start();
    segmentTimerRef.current = setTimeout(() => {
      if (recorder.state !== "inactive") recorder.stop();
    }, SEGMENT_DURATION_MS);
  };

  const finishStop = () => {
    setIsTranscribing(true);
    const ws = wsRef.current;
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({ type: "STOP_RECORDING" }));
    } else {
      setIsTranscribing(false);
    }
    streamRef.current?.getTracks().forEach((track) => track.stop());
    streamRef.current = null;
  };

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      streamRef.current = stream;

      const ws = new WebSocket(WEBSOCKET_BASE_URL);
      wsRef.current = ws;

      ws.onopen = () => {
        isRecordingRef.current = true;
        setIsRecording(true);
        recordSegment();
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (
            data.type === "partial_transcript" ||
            data.type === "final_transcript"
          ) {
            if (data.text) {
              setValue((prev) => (prev ? `${prev} ${data.text}` : data.text));
            }
            if (data.type === "final_transcript") {
              setIsTranscribing(false);
              ws.close();
            }
          } else if (data.type === "error") {
            console.error("Transcription error from server:", data.message);
            setIsTranscribing(false);
            ws.close();
          }
        } catch (e) {
          console.error("Failed to parse WS message", e);
        }
      };

      ws.onerror = () => {
        console.error("WebSocket error during transcription");
        isRecordingRef.current = false;
        setIsRecording(false);
        setIsTranscribing(false);
      };

      ws.onclose = () => {
        wsRef.current = null;
      };
    } catch (err) {
      console.error("Microphone access error", err);
    }
  };

  const stopRecording = () => {
    isRecordingRef.current = false;
    setIsRecording(false);

    if (segmentTimerRef.current) {
      clearTimeout(segmentTimerRef.current);
      segmentTimerRef.current = null;
    }

    const recorder = mediaRecorderRef.current;
    if (recorder && recorder.state !== "inactive") {
      recorder.stop(); // onstop sends the final blob, then finishStop() runs
    } else {
      finishStop();
    }
  };

  // Cleanup on unmount: stop any in-progress recording, release the mic, close the socket if user switch the page 
  useEffect(() => {
    return () => {
      isRecordingRef.current = false;
      if (segmentTimerRef.current) clearTimeout(segmentTimerRef.current);
      if (
        mediaRecorderRef.current &&
        mediaRecorderRef.current.state !== "inactive"
      ) {
        mediaRecorderRef.current.stop();
      }
      streamRef.current?.getTracks().forEach((track) => track.stop());
      wsRef.current?.close();
    };
  }, []);

  const handleSubmit = async () => {
    const content = value.trim();
    if (!content || disabled || isSending) return;
    setValue("");
    await onSend(content);
  };

  return (
    <div
      className={
        embedded
          ? "w-full"
          : "shrink-0 bg-white dark:bg-slate-950 p-3 pb-[max(0.75rem,env(safe-area-inset-bottom))] sm:p-4"
      }
    >
      <div className="relative mx-auto w-full max-w-4xl">
        <input
          type="text"
          value={value}
          placeholder={
            disabled
              ? "Loading conversation..."
              : isAnalystMode
                ? "Ask a question about your dataset..."
                : "Ask anything"
          }
          disabled={disabled || isSending}
          className="h-14 w-full rounded-2xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 py-3 pl-14 pr-28 text-sm text-slate-950 dark:text-white shadow-sm outline-none transition focus:border-cyan-500 dark:focus:border-cyan-500 focus:bg-white dark:focus:bg-slate-700 focus:ring-2 focus:ring-cyan-500/20 disabled:cursor-not-allowed disabled:bg-slate-100 dark:disabled:bg-slate-900 disabled:text-slate-400"
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
          isAnalystMode={isAnalystMode}
          onProcessMedia={onProcessMedia}
        />
        <button
          type="button"
          onClick={isRecording ? stopRecording : startRecording}
          disabled={disabled || isSending || isTranscribing}
          className={`absolute right-14 top-1/2 flex h-9 w-9 -translate-y-1/2 items-center justify-center rounded-xl transition ${
            isRecording
              ? "bg-red-500 text-white animate-pulse"
              : "bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-600"
          }`}
          aria-label={isRecording ? "Stop recording" : "Start recording"}
        >
          {isRecording ? (
            <MicOff className="h-4 w-4" />
          ) : (
            <Mic className="h-4 w-4" />
          )}
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
