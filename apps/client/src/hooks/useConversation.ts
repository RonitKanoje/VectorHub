import { useCallback, useRef, useState } from "react";
import toast from "react-hot-toast";
import api from "../services/api";
import { pollThreadStatus } from "../utils/pollThreadStatus";
import { getApiErrorMessage } from "../utils/errors";
import type { ChatMessage, Thread } from "../types";
import { store } from "../redux/store";

interface UseConversationReturn {
  messages: ChatMessage[];
  activeStatus: string | null;
  isLoadingConversation: boolean;
  isSending: boolean;
  setMessages: React.Dispatch<React.SetStateAction<ChatMessage[]>>;
  setActiveStatus: React.Dispatch<React.SetStateAction<string | null>>;
  loadConversation: (threadId: string, refresh?: boolean) => Promise<void>;
  handleSend: (
    content: string,
    activeThreadId: string | null,
    ensureActiveThread: () => string,
    setThreads: React.Dispatch<React.SetStateAction<Thread[]>>,
    isApproval?: boolean,
    isAnalystMode?: boolean,
  ) => Promise<void>;
}

let counter = 0;
function uniqueId(prefix: string) {
  return `${prefix}-${Date.now()}-${++counter}`;
}

export function useConversation(): UseConversationReturn {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [activeStatus, setActiveStatus] = useState<string | null>(null);
  const [isLoadingConversation, setIsLoadingConversation] = useState(false);
  const [isSending, setIsSending] = useState(false);

  const pollAbortRef = useRef<AbortController | null>(null);
  const messagesRef = useRef<ChatMessage[]>(messages);

  const updateMessages = useCallback(
    (updater: React.SetStateAction<ChatMessage[]>) => {
      setMessages((prev) => {
        const next = typeof updater === "function" ? updater(prev) : updater;
        messagesRef.current = next;
        return next;
      });
    },
    [],
  );

  const loadConversation = useCallback(
    async (threadId: string) => {
      pollAbortRef.current?.abort();
      pollAbortRef.current = null;

      setIsLoadingConversation(true);

      try {
        const [conversationResponse, statusResponse] = await Promise.all([
          api.get<{ messages: ChatMessage[] }>(`/api/ai/loadConv/${threadId}`),
          api.get<{ status: string }>(`/api/ai/thread_status/${threadId}`),
        ]);

        const loadedMessages = (conversationResponse.data.messages || []).map(
          (msg, idx) => ({
            ...msg,
            id: msg.id ?? `loaded-${threadId}-${idx}`,
          }),
        );

        updateMessages(loadedMessages);

        const status = statusResponse.data.status;
        setActiveStatus(status);

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
        updateMessages([]);
        setActiveStatus(null);
        toast.error("Could not load this conversation");
      } finally {
        setIsLoadingConversation(false);
      }
    },
    [updateMessages],
  );

  const handleSend = useCallback(
    async (
      content: string,
      activeThreadId: string | null,
      ensureActiveThread: () => string,
      setThreads: React.Dispatch<React.SetStateAction<Thread[]>>,
      isApproval: boolean = false,
      isAnalystMode: boolean = false,
    ) => {
      const threadId = ensureActiveThread();

      const isFirstUserMessage = messagesRef.current.every(
        (m) => m.role !== "user",
      );

      setIsSending(true);

      const userId = uniqueId("user");
      const assistantId = uniqueId("asst");

      updateMessages((prev) => {
        const next = [
          ...prev,
          { id: userId, role: "user" as const, content },
          {
            id: assistantId,
            role: "assistant" as const,
            content: "",
            pending: true,
          },
        ];
        return next;
      });

      try {
        const token = store.getState().auth.accessToken;
        const endpoint = isAnalystMode
          ? "/api/ai/analyst_chat"
          : "/api/ai/chat";
        const baseURL = api.defaults.baseURL || "http://localhost:3000";

        const response = await fetch(`${baseURL}${endpoint}`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({
            role: "user",
            content,
            thread_id: threadId,
            is_tool_approval: isApproval,
            message: content,
          }),
        });

        if (!response.ok) {
          throw new Error(`Request failed with status ${response.status}`);
        }

        setActiveStatus((status) => status || "chat");

        if (isFirstUserMessage) {
          api
            .post<{ title: string }>("/api/ai/nameChat", {
              message: content,
              thread_id: threadId,
            })
            .then((titleResponse) => {
              setThreads((prev) => [
                { thread_id: threadId, title: titleResponse.data.title },
                ...prev.filter((t) => t.thread_id !== threadId),
              ]);
            })
            .catch((e) => console.error("Could not name chat", e));
        }

        const reader = response.body?.getReader(); // stream reader 
        const decoder = new TextDecoder("utf-8"); // converting binary bytes to text
        if (!reader) throw new Error("No response body stream");

        updateMessages((prev) => {
          return prev.map((msg) =>
            msg.id === assistantId ? { ...msg, pending: false } : msg,
          );
        });

        let buffer = "";
        let aiResponseText = "";

        while (true) {
          const { done, value } = await reader.read(); // reads packets

          if (done) break;

          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split("\n");
          buffer = lines.pop() || ""; // removing half chunks 

          for (const line of lines) {
            if (!line.startsWith("data: ")) continue;
            const dataStr = line.slice(6);
            if (dataStr === "[DONE]") break;

            try {
              const data = JSON.parse(dataStr);

              if (data.type === "chunk") {
                aiResponseText += data.content;

                updateMessages((prev) =>
                  prev.map((msg) =>
                    msg.id === assistantId
                      ? { ...msg, content: aiResponseText, pending: false }
                      : msg,
                  ),
                );
              } else if (data.type === "approval") {
                updateMessages((prev) =>
                  prev.map((msg) =>
                    msg.id === assistantId
                      ? {
                          ...msg,
                          requires_approval: true,
                          tool: data.tool,
                          pending: false,
                        }
                      : msg,
                  ),
                );
              }
            } catch (e) {
              console.error("Failed to parse SSE line:", line, e);
            }
          }
        }
      } catch (error: unknown) {
        console.error("handleSend error:", error);
        const errorMsg = getApiErrorMessage(error, "Chat request failed");
        toast.error(errorMsg);
        updateMessages((prev) =>
          prev.map((msg) =>
            msg.id === assistantId && msg.pending
              ? { ...msg, content: errorMsg, pending: false }
              : msg,
          ),
        );
      } finally {
        setIsSending(false);
      }
    },
    [updateMessages],
  );

  return {
    messages,
    activeStatus,
    isLoadingConversation,
    isSending,
    setMessages: updateMessages,
    setActiveStatus,
    loadConversation,
    handleSend,
  };
}
