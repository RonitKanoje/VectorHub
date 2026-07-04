// ─── Thread domain types ──────────────────────────────────────────────────────

/** Chat mode selector for thread filtering. */
export type ThreadMode = "chat" | "analyst";

/** A chat thread entry shown in the sidebar. */
export interface Thread {
  thread_id: string;
  title: string;
}

export interface UseThreadsReturn {
  threads: Thread[]; // Thread id and title
  isLoadingThreads: boolean;
  loadThreads: (mode?: "chat" | "analyst") => Promise<void>; // it will return promise of type void
  handleNewChat: (
    setActiveThreadId: (id: string) => void,
    setActiveStatus: (status: string | null) => void,
    setMessages: (msgs: []) => void,
  ) => void;
  ensureActiveThread: (
    activeThreadId: string | null,
    setActiveThreadId: (id: string) => void,
  ) => string;
  setThreads: React.Dispatch<React.SetStateAction<Thread[]>>;
}