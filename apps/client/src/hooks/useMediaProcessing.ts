import { useRef, useState } from "react";
import toast from "react-hot-toast";
import api from "../services/api";
import { pollThreadStatus } from "../utils/pollThreadStatus";
import { getApiErrorMessage } from "../utils/errors";
import type { MediaPayload } from "../components/MessageInput";

interface UseMediaProcessingReturn {
  isProcessing: boolean;
  handleProcessMedia: (
    payload: MediaPayload,
    ensureActiveThread: () => string,
    removeDraftThread: (id: string) => void,
    setActiveStatus: (status: string | null) => void,
    loadThreads: () => Promise<void>,
  ) => Promise<void>;
}

export function useMediaProcessing(): UseMediaProcessingReturn {
  const [isProcessing, setIsProcessing] = useState(false);
  const pollAbortRef = useRef<AbortController | null>(null);

  const handleProcessMedia = async (
    payload: MediaPayload,
    ensureActiveThread: () => string,
    removeDraftThread: (id: string) => void,
    setActiveStatus: (status: string | null) => void,
    loadThreads: () => Promise<void>,
  ) => {
    const threadId = ensureActiveThread();
    setIsProcessing(true);
    setActiveStatus("queued");

    try {
      await api.post("/api/ai/process_media", {
        ...payload,
        thread_id: threadId,
        language: payload.language || null,
      });

      removeDraftThread(threadId);
      toast.success("Processing started");

      // Cancel any existing poll and start a fresh one
      pollAbortRef.current?.abort();
      const controller = new AbortController();
      pollAbortRef.current = controller;

      await pollThreadStatus(threadId, setActiveStatus, {
        signal: controller.signal,
      });

      await loadThreads();
    } catch (error: unknown) {
      const message = getApiErrorMessage(error, "Could not process media");
      toast.error(message);
      setActiveStatus("failed");
    } finally {
      setIsProcessing(false);
    }
  };

  return { isProcessing, handleProcessMedia };
}