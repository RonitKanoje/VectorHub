import { useCallback, useState } from "react";
import toast from "react-hot-toast";
import { useDispatch } from "react-redux";
import api from "../services/api";
import { setMessages } from "../redux/features/analystSlice";
import type { AppDispatch } from "../redux/store";
import type { AnalystChatMessage } from "../types/analyst";

export function useAnalystConversation() {
  const dispatch = useDispatch<AppDispatch>();
  const [isLoadingConversation, setIsLoadingConversation] = useState(false);

  const loadConversation = useCallback(
    async (threadId: string, isDraft: boolean) => {
      if (isDraft) {
        dispatch(setMessages([]));
        return;
      }

      setIsLoadingConversation(true);

      try {
        const response = await api.get<{ messages: AnalystChatMessage[] }>(
          `/api/ai/load_analyst_conv/${threadId}`
        );

        const loadedMessages = (response.data.messages || []).map(
          (msg, idx) => ({
            ...msg,
            id: msg.id ?? `loaded-${threadId}-${idx}`,
          })
        );

        dispatch(setMessages(loadedMessages));
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
