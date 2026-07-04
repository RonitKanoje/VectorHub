import { useCallback, useState } from "react";
import toast from "react-hot-toast";
import api from "../services/api";
import { createThreadId } from "../utils/createThreadId";
import type { Thread, UseThreadsReturn } from "../types";

export function useThreads(): UseThreadsReturn {
  const [threads, setThreads] = useState<Thread[]>([]);
  const [isLoadingThreads, setIsLoadingThreads] = useState(false);

  // using callback so that it does not call server everytime on rendering ui
  const loadThreads = useCallback(async (mode: "chat" | "analyst" = "chat") => {
    setIsLoadingThreads(true);
    try {
      const response = await api.get<Thread[]>(`/api/ai/threads?mode=${mode}`);
      const nextThreads = response.data || [];
      setThreads(nextThreads);
    } catch {
      toast.error("Could not load chat history");
    } finally {
      setIsLoadingThreads(false);
    }
  }, []);

  const handleNewChat = useCallback(
    (
      setActiveThreadId: (id: string) => void,
      setActiveStatus: (status: string | null) => void,
      setMessages: (msgs: []) => void,
    ) => {
      const threadId = createThreadId();
      setActiveThreadId(threadId);
      setActiveStatus(null);
      setMessages([]);
    },
    [],
  );

  const ensureActiveThread = useCallback(
    (
      activeThreadId: string | null,
      setActiveThreadId: (id: string) => void,
    ): string => {
      if (activeThreadId) return activeThreadId;

      const threadId = createThreadId();
      setActiveThreadId(threadId);
      return threadId;
    },
    [],
  );

  // in useThreads.ts return statement
  return {
    threads,
    isLoadingThreads,
    loadThreads,
    handleNewChat,
    ensureActiveThread,
    setThreads,
  };
}
