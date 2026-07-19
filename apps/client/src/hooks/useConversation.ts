import { useCallback, useRef, useState } from "react";
import toast from "react-hot-toast";
import api from "../services/api";
import { pollThreadStatus } from "../utils/pollThreadStatus";
import { getApiErrorMessage } from "../utils/errors";
import type { ChatMessage, Thread } from "../types";
import { store } from "../redux/store";
import type { UseConversationReturn } from "../types";
import { API_BASE_URL } from "../config/env";

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


  // we also have to update the messageRef therefore we are using useCallback to update the messages and messageRef at the same time
  const updateMessages = useCallback(
    (updater: React.SetStateAction<ChatMessage[]>) => { // React.SetStateAction<T> is the type React uses for state updates. It allows the updater to be either a new state value of type T or a callback function that receives the previous state and returns the next state. This matches how React's setState functions work
      setMessages((prev) => {
        const next = typeof updater === "function" ? updater(prev) : updater;
        messagesRef.current = next;
        return next;
      });
    },
    [],
  );

  const abortStatusPolling = useCallback(() => {
    pollAbortRef.current?.abort();
    pollAbortRef.current = null;
  }, []);

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

        // Only poll while ingestion is actually in progress
        const processingStatuses = ["queued", "processing", "pending"];

        if (processingStatuses.includes(status)) {
          const controller = new AbortController();
          pollAbortRef.current = controller;

          pollThreadStatus(threadId, setActiveStatus, controller.signal).catch(
            () => {
              setActiveStatus("failed");
              toast.error("Processing failed");
            },
          );
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
      _activeThreadId: string | null,
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

      // -----------------------------------------------------------------
      // Message ID resolution.
      //
      // Normal send: allocate fresh ids for a new user + assistant pair.
      //
      // Tool approval: we must NOT add a new user message ("yes") to the
      // visible conversation — it is an internal signal to the graph, not
      // a human turn. We also must NOT create a new assistant bubble.
      // Instead we find the existing assistant message that currently holds
      // the approval card (requires_approval === true) and stream the final
      // answer directly into it, replacing the approval UI in-place.
      // -----------------------------------------------------------------
      let assistantId: string;

      if (isApproval) {
        // Find the last assistant message that is awaiting approval.
        const approvalMsg = [...messagesRef.current]
          .reverse()
          .find((m) => m.role === "assistant" && m.requires_approval);

        if (approvalMsg) {
          assistantId = approvalMsg.id;
          // Clear approval state and set the bubble back to pending while
          // we wait for the resumed graph to produce its answer.
          updateMessages((prev) =>
            prev.map((msg) =>
              msg.id === assistantId
                ? {
                    ...msg,
                    requires_approval: false,
                    tool: undefined,
                    content: "",
                    pending: true,
                  }
                : msg,
            ),
          );
        } else {
          // Fallback: no approval message found, create a fresh assistant bubble.
          assistantId = uniqueId("asst");
          updateMessages((prev) => [
            ...prev,
            { id: assistantId, role: "assistant" as const, content: "", pending: true },
          ]);
        }
      } else {
        // Normal user message: push visible user turn + blank assistant bubble.
        const userId = uniqueId("user");
        assistantId = uniqueId("asst");

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
      }

      try {
        const token = store.getState().auth.accessToken;
        const endpoint = isAnalystMode
          ? "/api/ai/analyst_chat"
          : "/api/ai/chat";
        // We intentionally use native fetch() instead of Axios here.
        // Axios traditionally downloads the whole response and its support for Server-Sent Events (SSE)
        // streams in the browser is difficult to handle reliably without losing chunks.
        // fetch() provides native stream readers which are essential for this streaming feature.
        const response = await fetch(`${API_BASE_URL}${endpoint}`, {
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

        if (isFirstUserMessage && !isApproval) {
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
          const { done, value } = await reader.read(); // reads packets done => boolean, value => Uint8Array

          if (done) break;

          buffer += decoder.decode(value, { stream: true }); // decode the binary data to text
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
    abortStatusPolling,
    handleSend,
  };
}
