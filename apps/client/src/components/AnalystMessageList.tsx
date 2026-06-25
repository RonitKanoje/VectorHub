import { useEffect, useRef } from "react";
import AnalystEmptyState from "./AnalystEmptyState";
import AnalystChatMessage from "./AnalystChatMessage";
import AnalystSystemMessage from "./AnalystSystemMessage";
import type { AnalystChatMessage as AnalystChatMessageType } from "../types/analyst";

interface AnalystMessageListProps {
  messages: AnalystChatMessageType[];
}

const AnalystMessageList = ({ messages }: AnalystMessageListProps) => {
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    scrollRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  if (messages.length === 0) {
    return (
      <div className="flex-1 overflow-y-auto bg-slate-950 px-4 py-6 flex items-center justify-center">
        <AnalystEmptyState />
      </div>
    );
  }

  return (
    <div className="flex-1 overflow-y-auto bg-slate-950 px-4 py-6">
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