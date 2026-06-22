import { useEffect, useRef } from "react";
import AnalystEmptyState from "./AnalystEmptyState";
import AnalystChatMessage from "./AnalystChatMessage";
import AnalystSystemMessage from "./AnalystSystemMessage";
import type { AnalystChatMessage as AnalystChatMessageType } from "../types/analyst";

interface AnalystMessageListProps {
  messages: AnalystChatMessageType[];
  onSelectPrompt: (prompt: string) => void;
}

const AnalystMessageList = ({ messages, onSelectPrompt }: AnalystMessageListProps) => {
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    scrollRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  return (
    <div className="flex-1 overflow-y-auto bg-slate-950 px-4 py-6">
      {messages.length === 0 && <AnalystEmptyState onSelectPrompt={onSelectPrompt} />}

      <div className="mx-auto flex max-w-4xl flex-col gap-4">
        {messages.map((msg) =>
          msg.role === "system" ? (
            <AnalystSystemMessage key={msg.id} message={msg} />
          ) : (
            <AnalystChatMessage key={msg.id} message={msg} />
          ),
        )}
        <div ref={scrollRef} />
      </div>
    </div>
  );
};

export default AnalystMessageList;