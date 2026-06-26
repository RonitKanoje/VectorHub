import { useCallback, useState } from "react";
import toast from "react-hot-toast";
import { useDispatch } from "react-redux";
import api from "../services/api";
import { setMessages } from "../redux/features/analystSlice";
import type { AppDispatch } from "../redux/store";
import type { AnalystMessage } from "../types";
import { store } from "../redux/store";

export function useAnalystConversation() {
  const dispatch = useDispatch<AppDispatch>();
  const [isLoadingConversation, setIsLoadingConversation] = useState(false);

  const loadConversation = useCallback(
    async (threadId: string) => {
      setIsLoadingConversation(true);

      try {
        const response = await api.get<{ messages: AnalystMessage[] }>(
          `/api/ai/load_analyst_conv/${threadId}`
        );

        const serverMessages = (response.data.messages || []).map(
          (msg, idx) => ({
            ...msg,
            id: msg.id ?? `loaded-${threadId}-${idx}`,
          })
        );

        if (serverMessages.length === 0) {
          // Nothing persisted yet — keep whatever is in Redux (e.g. streamed state)
          return;
        }

        // Merge: for each assistant message from the server, carry over any
        // visualizations that are already in Redux state. This prevents the
        // reload from stripping charts that were streamed but not yet stored
        // in the LangGraph checkpointer.
        const currentMessages = store.getState().analyst.messages;

        const merged = serverMessages.map((serverMsg) => {
          if (serverMsg.role !== "assistant") return serverMsg;

          // Find the matching assistant message in Redux by position
          // (messages alternate user/assistant so index math is reliable)
          const idx = serverMessages.indexOf(serverMsg);
          const reduxMsg = currentMessages[idx];

          const hasServerViz =
            serverMsg.visualizations && serverMsg.visualizations.length > 0;
          const hasReduxViz =
            reduxMsg?.visualizations && reduxMsg.visualizations.length > 0;

          if (!hasServerViz && hasReduxViz) {
            // Server doesn't have the viz yet — keep the streamed one
            return { ...serverMsg, visualizations: reduxMsg.visualizations };
          }

          return serverMsg;
        });

        dispatch(setMessages(merged));
      } catch {
        dispatch(setMessages([]));
        toast.error("Could not load this conversation");
      } finally {
        setIsLoadingConversation(false);
      }
    },
    [dispatch]
  );

  return {
    isLoadingConversation,
    loadConversation,
  };
}
