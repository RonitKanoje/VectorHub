import { useCallback, useState } from "react";
import toast from "react-hot-toast";
import api from "../services/api";
import { createThreadId } from "../utils/createThreadId";
import type { ChatThread } from "../components/ChatSidebar";

interface UseThreadsReturn {
  threads: ChatThread[]; // Thread id and title
  isLoadingThreads: boolean;
  draftThreadIds: Set<string>;
  loadThreads: () => Promise<void>; // it will return promise of type void
  handleNewChat: (
    setActiveThreadId: (id: string) => void,
    setActiveStatus: (status: string | null) => void,
    setMessages: (msgs: []) => void,
  ) => void;
  ensureActiveThread: (
    activeThreadId: string | null,
    setActiveThreadId: (id: string) => void,
  ) => string;
  removeDraftThread: (threadId: string) => void;
  setThreads: React.Dispatch<React.SetStateAction<ChatThread[]>>; // SetStateAction<T> = T | ((prevState: T) => T); and dispatch is a function that takes input and returns nothing
  setDraftThreadIds: React.Dispatch<React.SetStateAction<Set<string>>>; // ← add this
}

export function useThreads(): UseThreadsReturn {
  const [threads, setThreads] = useState<ChatThread[]>([]);
  const [isLoadingThreads, setIsLoadingThreads] = useState(false);
  const [draftThreadIds, setDraftThreadIds] = useState<Set<string>>(
    () => new Set(),
  );

  // using callback so that it does not call server everytime on rendering of the ui
  const loadThreads = useCallback(async () => {
    setIsLoadingThreads(true);
    try {
      const response = await api.get<ChatThread[]>("/api/ai/threads");
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
      setDraftThreadIds((prev) => new Set(prev).add(threadId));
      setThreads((prev) => [
        { thread_id: threadId, title: "New Chat" },
        ...prev,
      ]);
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
      setDraftThreadIds((prev) => new Set(prev).add(threadId));
      setThreads((prev) => [
        { thread_id: threadId, title: "New Chat" },
        ...prev,
      ]);
      setActiveThreadId(threadId);
      return threadId;
    },
    [],
  );

  const removeDraftThread = useCallback((threadId: string) => {
    setDraftThreadIds((prev) => {
      const next = new Set(prev);
      next.delete(threadId);
      return next;
    });
  }, []);

  // in useThreads.ts return statement
  return {
    threads,
    isLoadingThreads,
    draftThreadIds,
    loadThreads,
    handleNewChat,
    ensureActiveThread,
    removeDraftThread,
    setThreads,
    setDraftThreadIds, // ← add this
  };
}
