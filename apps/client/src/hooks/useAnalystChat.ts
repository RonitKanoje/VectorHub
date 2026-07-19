import { useCallback } from "react";
import toast from "react-hot-toast";
import { useDispatch } from "react-redux";
import api from "../services/api";
import {
  addUserMessage,
  appendChunk,
  appendVisualization,
  finalizeResponse,
  setError,
  setIsSending,
} from "../redux/features/analystSlice";
import type { AppDispatch } from "../redux/store";
import { store } from "../redux/store";
import { API_BASE_URL } from "../config/env";

/**
 * Encapsulates sending a message + reading the streamed SSE response
 * from /api/ai/analyst_chat, dispatching chunks into Redux as they arrive.
 */
export const useAnalystChat = (token: string | null) => {
  const dispatch = useDispatch<AppDispatch>();

  const handleSend = useCallback(
    async (
      content: string,
      threadId: string,
      setThreads: React.Dispatch<React.SetStateAction<any[]>>
    ) => {
      if (!content.trim()) return;

      dispatch(addUserMessage(content));

      dispatch(setIsSending(true));

      try {
        const response = await fetch(`${API_BASE_URL}/api/ai/analyst_chat`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({
            role: "user",
            content,
            thread_id: threadId,
            message: content,
          }),
        });

        if (!response.ok) {
          throw new Error(`Request failed with status ${response.status}`);
        }

        // Try to name the chat on the first message
        const isFirstMessage = store.getState().analyst.messages.length === 2; // user + pending assistant
        if (isFirstMessage) {
          api
            .post<{ title: string }>("/api/ai/nameChat", {
              message: content,
              thread_id: threadId,
            })
            .then((titleResponse) => {
              setThreads((prev) => [
                { thread_id: threadId, title: titleResponse.data.title },
                ...prev.filter(t => t.thread_id !== threadId),
              ]);
            })
            .catch((e) => console.error("Could not name chat", e));
        }

        const reader = response.body?.getReader(); // stream reader 
        const decoder = new TextDecoder("utf-8"); // stream returns raw bytes and here we are decoding it 

        if (!reader) {
          throw new Error("No response body stream");
        }

        let buffer = "";

        while (true) {
          const { done, value } = await reader.read();

          if (done) break;

          buffer += decoder.decode(value, { stream: true });

          const lines = buffer.split("\n");
          buffer = lines.pop() || "";

          for (const line of lines) {
            if (!line.startsWith("data: ")) continue;

            const dataStr = line.slice(6);

            if (dataStr === "[DONE]") {
              break;
            }

            try {
              const data = JSON.parse(dataStr);

              if (data.type === "chunk") {
                dispatch(appendChunk(data.content));
              } else if (data.type === "visualization") {
                dispatch(appendVisualization(data));
              } else if (data.type === "progress") {
                dispatch(appendChunk(`\n_${data.content}_\n`));
              } else if (data.type === "tool") {
                dispatch(appendChunk(`\n> ${data.content}\n`));
              } else if (data.type === "profile") {
                dispatch(appendChunk(`\n${data.content}\n`));
              }
            } catch {
              // Ignore malformed chunks
            }
          }
        }

        dispatch(finalizeResponse());
      } catch (error: unknown) {
        const errorMsg =
          error instanceof Error ? error.message : "Chat request failed";

        toast.error(errorMsg);

        dispatch(setError(errorMsg));
      } finally {
        dispatch(setIsSending(false));
      }
    },
    [dispatch, token],
  );

  return { handleSend };
};
