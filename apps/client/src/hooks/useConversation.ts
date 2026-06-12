import { useCallback, useRef, useState } from "react";
import toast from "react-hot-toast";
import api from "../services/api";
import { pollThreadStatus } from "../utils/pollThreadStatus";
import { getApiErrorMessage } from "../utils/errors";
import type { ChatMessage } from "../components/ChatMessagePanel";
import type { ChatThread } from "../components/ChatSidebar";

interface UseConversationReturn {
  messages: ChatMessage[];
  activeStatus: string | null;
  isLoadingConversation: boolean;
  isSending: boolean;
  setMessages: React.Dispatch<React.SetStateAction<ChatMessage[]>>;
  setActiveStatus: React.Dispatch<React.SetStateAction<string | null>>;
  loadConversation: (threadId: string, isDraft: boolean) => Promise<void>;
  handleSend: (
    content: string,
    activeThreadId: string | null,
    ensureActiveThread: () => string,
    removeDraftThread: (id: string) => void,
    setThreads: React.Dispatch<React.SetStateAction<ChatThread[]>>,
  ) => Promise<void>;
}

export function useConversation(): UseConversationReturn {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [activeStatus, setActiveStatus] = useState<string | null>(null);
  const [isLoadingConversation, setIsLoadingConversation] = useState(false);
  const [isSending, setIsSending] = useState(false);

  // Abort controller so we cancel stale polls when the user switches threads
  const pollAbortRef = useRef<AbortController | null>(null); // object that can cancel aynchronous operations

  const loadConversation = useCallback(
    async (threadId: string, isDraft: boolean) => {
      // Cancel any in-flight poll from a previous thread
      pollAbortRef.current?.abort();
      pollAbortRef.current = null;

      if (isDraft) {
        setMessages([]);
        setActiveStatus(null);
        return;
      }

      setIsLoadingConversation(true);

      try {
        const [conversationResponse, statusResponse] = await Promise.all([
          api.get<{ messages: ChatMessage[] }>(`/api/ai/loadConv/${threadId}`),
          api.get<{ status: string }>(`/api/ai/thread_status/${threadId}`),
        ]);

        setMessages(conversationResponse.data.messages || []);

        const status = statusResponse.data.status;
        setActiveStatus(status);

        // Resume polling if the job is still running
        if (status !== "completed" && !status.startsWith("failed")) {
          const controller = new AbortController();
          pollAbortRef.current = controller;

          pollThreadStatus(threadId, setActiveStatus, {
            signal: controller.signal,
          }).catch(() => {
            setActiveStatus("failed");
            toast.error("Processing failed");
          });
        }
      } catch {
        setMessages([]);
        setActiveStatus(null);
        toast.error("Could not load this conversation");
      } finally {
        setIsLoadingConversation(false);
      }
    },
    [],
  );

  const handleSend = useCallback(
    async (
      content: string,
      activeThreadId: string | null,
      ensureActiveThread: () => string,
      removeDraftThread: (id: string) => void,
      setThreads: React.Dispatch<React.SetStateAction<ChatThread[]>>,
    ) => {
      const threadId = ensureActiveThread();
      const isFirstUserMessage = messages.every((m) => m.role !== "user");  /// 

      setIsSending(true);
      setMessages((prev) => [
        ...prev,
        { role: "user", content },
        { role: "assistant", content: "Thinking...", pending: true },
      ]);

      try {
        const response = await api.post<{ response: string }>("/api/ai/chat", {
          role: "user",
          content,
          thread_id: threadId,
        });

        setActiveStatus((status) => status || "chat");
        removeDraftThread(threadId);

        setMessages((prev) =>
          prev.map((message, index) =>
            index === prev.length - 1 && message.pending
              ? { role: "assistant", content: response.data.response }
              : message,
          ),
        );

        if (isFirstUserMessage) {
          const titleResponse = await api.post<{ title: string }>(
            "/api/ai/nameChat",
            { message: content, thread_id: threadId },
          );
          setThreads((prev) =>
            prev.map((thread) =>
              thread.thread_id === threadId
                ? { ...thread, title: titleResponse.data.title }
                : thread,
            ),
          );
        }
      } catch (error: unknown) {
        const message = getApiErrorMessage(error, "Chat request failed");
        toast.error(message);
        setMessages((prev) =>
          prev.map((item, index) =>
            index === prev.length - 1 && item.pending
              ? { role: "assistant", content: message }
              : item,
          ),
        );
      } finally {
        setIsSending(false);
      }
    },
    [messages],
  );

  return {
    messages,
    activeStatus,
    isLoadingConversation,
    isSending,
    setMessages,
    setActiveStatus,
    loadConversation,
    handleSend,
  };
}