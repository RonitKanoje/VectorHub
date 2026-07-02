import { useEffect, useRef } from "react";
import MessageBubble from "./MessageBubble";
import type { ChatMessage, AnalystMessage } from "../types";

interface MessageListProps {
  messages: Array<ChatMessage | AnalystMessage>;
  isAnalystMode?: boolean;
  onSend?: (content: string, isApproval?: boolean) => Promise<void>;
}

const MessageList = ({
  messages,
  isAnalystMode = false,
  onSend,
}: MessageListProps) => {
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    scrollRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  if (messages.length === 0) {
    return (
      <div className="flex-1 flex items-center justify-center px-4 py-6 bg-white dark:bg-slate-950">
        <div className="max-w-2xl rounded-2xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-900 px-6 py-5 text-center">
          <h3 className="text-lg font-semibold text-slate-800 dark:text-slate-100">
            {isAnalystMode
              ? "✅ Dataset processed successfully"
              : "✅ Content processed successfully"}
          </h3>

          <p className="mt-2 text-sm text-slate-600 dark:text-slate-400">
            {isAnalystMode
              ? "Your dataset has been analyzed and is ready. You can now ask questions about the data, request charts, statistics, summaries, trends, or insights."
              : "Your content has been processed successfully. You can now ask anything about the uploaded file, video, audio, PDF, or YouTube video."}
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 overflow-y-auto px-4 py-6 bg-white dark:bg-slate-950">
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
    </div>
  );
};

export default MessageList;
