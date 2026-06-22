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
    isApproval?: boolean,
    isAnalystMode?: boolean,
  ) => Promise<void>;
}

import { store } from "../redux/store";

let _counter = 0;
function uniqueId(prefix: string) {
  return `${prefix}-${Date.now()}-${++_counter}`;
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
    async (threadId: string, isDraft: boolean) => {
      pollAbortRef.current?.abort();
      pollAbortRef.current = null;

      if (isDraft) {
        updateMessages([]);
        setActiveStatus(null);
        return;
      }

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

        console.log("📦 Loaded messages from server:", loadedMessages);

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
      removeDraftThread: (id: string) => void,
      setThreads: React.Dispatch<React.SetStateAction<ChatThread[]>>,
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

      console.log("🟡 Generated IDs:", { userId, assistantId });

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
        console.log(
          "🟢 Messages after user+assistant added:",
          next.map((m) => ({
            id: m.id,
            role: m.role,
            content: m.content?.slice(0, 30),
          })),
        );
        return next;
      });

      try {
        const token = store.getState().auth.accessToken;
        const endpoint = isAnalystMode
          ? "/api/ai/analyst_chat"
          : "/api/ai/chat";
        const baseURL = api.defaults.baseURL || "http://localhost:3000";

        console.log("📤 Sending request to:", `${baseURL}${endpoint}`);

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

        console.log("📥 Response status:", response.status);

        if (!response.ok) {
          throw new Error(`Request failed with status ${response.status}`);
        }

        setActiveStatus((status) => status || "chat");
        removeDraftThread(threadId);

        if (isFirstUserMessage) {
          api
            .post<{ title: string }>("/api/ai/nameChat", {
              message: content,
              thread_id: threadId,
            })
            .then((titleResponse) => {
              setThreads((prev) =>
                prev.map((thread) =>
                  thread.thread_id === threadId
                    ? { ...thread, title: titleResponse.data.title }
                    : thread,
                ),
              );
            })
            .catch((e) => console.error("Could not name chat", e));
        }

        const reader = response.body?.getReader();
        const decoder = new TextDecoder("utf-8");
        if (!reader) throw new Error("No response body stream");

        console.log("✅ Stream reader obtained, clearing pending...");

        updateMessages((prev) => {
          const found = prev.find((m) => m.id === assistantId);
          console.log(
            "🔍 Clearing pending — assistantId found?",
            !!found,
            "assistantId:",
            assistantId,
          );
          return prev.map((msg) =>
            msg.id === assistantId ? { ...msg, pending: false } : msg,
          );
        });

        let buffer = "";
        let aiResponseText = "";
        let chunkCount = 0;

        while (true) {
          const { done, value } = await reader.read();
          if (done) {
            console.log(
              "🏁 Stream done. Total chunks:",
              chunkCount,
              "Final text:",
              aiResponseText.slice(0, 100),
            );
            break;
          }

          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split("\n");
          buffer = lines.pop() || "";

          for (const line of lines) {
            if (!line.startsWith("data: ")) continue;
            const dataStr = line.slice(6);
            if (dataStr === "[DONE]") {
              console.log("✅ [DONE] received");
              break;
            }

            try {
              const data = JSON.parse(dataStr);
              console.log("📨 Parsed SSE event type:", data.type);

              if (data.type === "chunk") {
                chunkCount++;
                aiResponseText += data.content;

                if (chunkCount <= 3) {
                  console.log(`🔵 Chunk #${chunkCount}:`, data.content);
                }

                updateMessages((prev) => {
                  const found = prev.find((m) => m.id === assistantId);
                  if (chunkCount <= 3) {
                    console.log(
                      `🔵 Chunk #${chunkCount} — assistantId "${assistantId}" found in prev?`,
                      !!found,
                      "prev ids:",
                      prev.map((m) => m.id),
                    );
                  }
                  return prev.map((msg) =>
                    msg.id === assistantId
                      ? { ...msg, content: aiResponseText, pending: false }
                      : msg,
                  );
                });
              } else if (data.type === "approval") {
                console.log("🟠 Approval event received:", data.tool);
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
              } else {
                console.log("❓ Unknown event type:", data.type, data);
              }
            } catch (e) {
              console.warn("⚠️ Failed to parse SSE line:", line, e);
            }
          }
        }
      } catch (error: unknown) {
        console.error("❌ handleSend error:", error);
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
