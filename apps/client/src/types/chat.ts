// ─── Chat domain types ────────────────────────────────────────────────────────

import type { Thread } from "./thread";

export type ChatRole = "user" | "assistant";

/** Shared media attachment pill shown on messages in both Chat and Analyst. */
export interface MediaAttachment {
  type: string;
  name: string;
}

/** A single message in the main (RAG) chat conversation. */
export interface ChatMessage {
  id: string;
  role: ChatRole;
  content: string;
  pending?: boolean;
  requires_approval?: boolean;
  tool?: string;
  mediaAttachment?: MediaAttachment;
}

export interface UseConversationReturn {
  messages: ChatMessage[];
  activeStatus: string | null;
  isLoadingConversation: boolean;
  isSending: boolean;
  setMessages: React.Dispatch<React.SetStateAction<ChatMessage[]>>;
  setActiveStatus: React.Dispatch<React.SetStateAction<string | null>>;
  loadConversation: (threadId: string, refresh?: boolean) => Promise<void>;
  abortStatusPolling: () => void;
  handleSend: (
    content: string,
    activeThreadId: string | null,
    ensureActiveThread: () => string,
    setThreads: React.Dispatch<React.SetStateAction<Thread[]>>,
    isApproval?: boolean,
    isAnalystMode?: boolean,
  ) => Promise<void>;
}

export interface ChatSidebarProps {
  isSidebarOpen: boolean;
  onToggleSidebar: () => void;
  threads: Thread[];
  activeThreadId: string | null;
  isLoadingThreads: boolean;
  onNewChat: () => void;
  onSelectThread: (threadId: string) => void;
  onLogout: () => void;
  onLogoutAll: () => void;
}