import { useRef, useState } from "react";
import toast from "react-hot-toast";
import api from "../services/api";
import { pollThreadStatus } from "../utils/pollThreadStatus";
import { getApiErrorMessage } from "../utils/errors";
import type { MediaPayload } from "../types";

interface UseMediaProcessingReturn {
  isProcessing: boolean;
  resetProcessing: () => void;
  handleProcessMedia: (
    payload: MediaPayload,
    ensureActiveThread: () => string,
    setActiveStatus: (status: string | null) => void,
    loadThreads: () => Promise<void>,
  ) => Promise<void>;
}

export function useMediaProcessing(): UseMediaProcessingReturn {
  const [isProcessing, setIsProcessing] = useState(false);
  const pollAbortRef = useRef<AbortController | null>(null);

  const resetProcessing = () => {
    pollAbortRef.current?.abort();
    pollAbortRef.current = null;
    setIsProcessing(false);
  };

  const handleProcessMedia = async (
    payload: MediaPayload,
    ensureActiveThread: () => string,
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

      try {
        await api.post("/api/ai/nameThreadFromUpload", {
          thread_id: threadId,
          media: payload.media,
          filename: payload.file?.name || payload.path || "Upload",
        });
      } catch (err) {
        console.error("Failed to name thread from upload", err);
      }

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

  return { isProcessing, resetProcessing, handleProcessMedia };
}