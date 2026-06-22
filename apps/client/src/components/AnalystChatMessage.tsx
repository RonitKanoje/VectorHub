import { Bot, User } from "lucide-react";
import type { AnalystChatMessage as AnalystChatMessageType } from "../types/analyst";

interface AnalystChatMessageProps {
  message: AnalystChatMessageType;
}

const AnalystChatMessage = ({ message }: AnalystChatMessageProps) => {
  const isUser = message.role === "user";

  return (
    <div className={`flex gap-3 ${isUser ? "justify-end" : "justify-start"}`}>
      {!isUser && (
        <div className="mt-1 flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-violet-700 text-white">
          <Bot className="h-4 w-4" />
        </div>
      )}
      <div
        className={`max-w-[78%] rounded-2xl px-4 py-3 text-sm leading-6 shadow-sm ${
          isUser
            ? "bg-violet-700 text-white"
            : "border border-slate-700 bg-slate-800 text-slate-100"
        } ${message.pending ? "animate-pulse opacity-70" : ""}`}
      >
        <span className="whitespace-pre-wrap">
          {message.content || (message.pending ? "Analysing…" : "")}
        </span>
      </div>
      {isUser && (
        <div className="mt-1 flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-violet-900/60 text-violet-300">
          <User className="h-4 w-4" />
        </div>
      )}
    </div>
  );
};

export default AnalystChatMessage;