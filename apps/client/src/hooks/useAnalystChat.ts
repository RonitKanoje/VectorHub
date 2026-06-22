import { useCallback } from "react";
import toast from "react-hot-toast";
import { useDispatch } from "react-redux";
import api from "../services/api";
import {
  addUserMessage,
  appendChunk,
  finalizeResponse,
  setError,
  setIsSending,
} from "../redux/features/analystSlice";
import type { AppDispatch } from "../redux/store";

/**
 * Encapsulates sending a message + reading the streamed SSE response
 * from /api/ai/analyst_chat, dispatching chunks into Redux as they arrive.
 */
export const useAnalystChat = (threadId: string, token: string | null) => {
  const dispatch = useDispatch<AppDispatch>();

  const handleSend = useCallback(
    async (content: string) => {
      if (!content.trim()) return;

      dispatch(addUserMessage(content));

      dispatch(setIsSending(true));

      try {
        const baseURL = api.defaults.baseURL || "http://localhost:3000";

        const response = await fetch(`${baseURL}/api/ai/analyst_chat`, {
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
    [dispatch, token, threadId],
  );

  return { handleSend };
};
