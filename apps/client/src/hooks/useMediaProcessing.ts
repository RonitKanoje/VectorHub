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
      let data: FormData | Record<string, any>;
      let config = {};

      if (payload.file) {
        const formData = new FormData();
        formData.append("file", payload.file);
        formData.append("media", payload.media);
        formData.append("thread_id", threadId);
        if (payload.language) formData.append("language", payload.language);
        if (payload.path) formData.append("path", payload.path);
        
        data = formData;
        config = { headers: { "Content-Type": "multipart/form-data" } };
      } else {
        data = {
          ...payload,
          thread_id: threadId,
          language: payload.language || null,
        };
      }

      await api.post("/api/upload", data, config);

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