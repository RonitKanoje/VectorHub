import { useEffect, useRef } from "react";
import EmptyState from "./EmptyState";
import MessageBubble from "./MessageBubble";
import type { ChatMessage, AnalystMessage } from "../types";

interface MessageListProps {
  messages: Array<ChatMessage | AnalystMessage>;
  isAnalystMode?: boolean;
  onSend?: (content: string, isApproval?: boolean) => Promise<void>;
}

const MessageList = ({ messages, isAnalystMode = false, onSend }: MessageListProps) => {
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    scrollRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  return (
    <div className={`flex-1 overflow-y-auto px-4 py-6 ${isAnalystMode ? "bg-slate-950" : "bg-white dark:bg-slate-950"}`}>
      {messages.length === 0 ? (
        <EmptyState isAnalystMode={isAnalystMode} />
      ) : (
        <div className="mx-auto flex max-w-4xl flex-col gap-4">
          {messages.map((msg, idx) => (
            <MessageBubble
              key={msg.id ?? `msg-${idx}`}
              message={msg}
              isAnalystMode={isAnalystMode}
              onSend={onSend}
              isLast={idx === messages.length - 1}
            />
          ))}
          <div ref={scrollRef} />
        </div>
      )}
    </div>
  );
};

export default MessageList;
