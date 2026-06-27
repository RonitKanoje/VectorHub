import ReactMarkdown from "react-markdown";
import {
  Check,
  X,
  FileText,
  Video,
  Mic,
  FileBarChart,
  Link,
  Play,
} from "lucide-react";
import type { ChatMessage, AnalystMessage } from "../types";

interface MessageBubbleProps {
  message: ChatMessage | AnalystMessage;
  isAnalystMode?: boolean;
  onSend?: (content: string, isApproval?: boolean) => Promise<void>;
  isLast?: boolean;
}

const MessageBubble = ({
  message,
  isAnalystMode,
  onSend,
  isLast,
}: MessageBubbleProps) => {
  const isUser = message.role === "user";
  const isPending = "pending" in message && message.pending;
  const isApproval =
    "requires_approval" in message && message.requires_approval;

  const getMediaIcon = (type: string) => {
    switch (type) {
      case "video":
        return <Video className="h-4 w-4" />;
      case "audio":
        return <Mic className="h-4 w-4" />;
      case "document":
        return <FileText className="h-4 w-4" />;
      case "dataset":
        return <FileBarChart className="h-4 w-4" />;
      case "youtube":
        return <Play className="h-4 w-4" />;
      default:
        return <Link className="h-4 w-4" />;
    }
  };

  return (
    <div
      className={`flex w-full ${isUser ? "justify-end" : "justify-start"} animate-in fade-in slide-in-from-bottom-2`}
    >
      <div
        className={`max-w-[85%] rounded-2xl px-5 py-4 ${isUser ? "bg-slate-900 text-white dark:bg-slate-700 dark:text-white shadow-sm" : "bg-slate-100 dark:bg-slate-800 text-slate-800 dark:text-slate-200 shadow-sm"}`}
      >
        {!isUser && isAnalystMode && (
          <div className="mb-2 flex items-center gap-2 text-sm font-medium text-violet-600 dark:text-violet-400">
            <div className="flex h-6 w-6 items-center justify-center rounded-full bg-violet-100 dark:bg-violet-900/30">
              ✨
            </div>
            Data Analyst
          </div>
        )}

        {!isUser && !isAnalystMode && (
          <div className="mb-2 flex items-center gap-2 text-sm font-medium text-slate-600 dark:text-slate-400">
            Assistant
          </div>
        )}

        <div className="prose prose-sm dark:prose-invert max-w-none break-words">
          {message.content ? (
            <ReactMarkdown>{message.content}</ReactMarkdown>
          ) : isPending ? (
            <div className="flex space-x-1 items-center h-4">
              <div className="w-1.5 h-1.5 bg-slate-400 rounded-full animate-bounce [animation-delay:-0.3s]"></div>
              <div className="w-1.5 h-1.5 bg-slate-400 rounded-full animate-bounce [animation-delay:-0.15s]"></div>
              <div className="w-1.5 h-1.5 bg-slate-400 rounded-full animate-bounce"></div>
            </div>
          ) : null}
        </div>

        {"mediaAttachment" in message && message.mediaAttachment && (
          <div className="mt-3 flex items-center gap-2 rounded-lg bg-black/10 px-3 py-2 text-sm">
            {getMediaIcon(message.mediaAttachment.type)}
            <span className="truncate">{message.mediaAttachment.name}</span>
          </div>
        )}

        {isAnalystMode &&
          "visualizations" in message &&
          message.visualizations &&
          Object.keys(message.visualizations).length > 0 && (
            <div className="mt-4 flex flex-col gap-4">
              {Object.entries(message.visualizations).map(([name, base64]) => (
                <div
                  key={name}
                  className="overflow-hidden rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900"
                >
                  <div className="border-b border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 px-3 py-2 text-xs font-medium text-slate-500 dark:text-slate-400">
                    {name}
                  </div>
                  <img
                    src={`data:image/png;base64,${base64}`}
                    alt={name}
                    className="w-full h-auto object-contain p-2"
                  />
                </div>
              ))}
            </div>
          )}

        {isApproval && onSend && isLast && (
          <div className="mt-4 flex items-center gap-3 rounded-lg border border-cyan-200 bg-cyan-50 p-3 dark:border-cyan-900 dark:bg-cyan-900/20">
            <div className="flex-1 text-sm text-cyan-800 dark:text-cyan-200">
              Tool needs approval:{" "}
              <span className="font-semibold">
                {("tool" in message && message.tool) || "Unknown Tool"}
              </span>
            </div>
            <div className="flex gap-2">
              <button
                onClick={() => onSend("yes", true)}
                className="flex items-center gap-1 rounded bg-cyan-600 px-3 py-1.5 text-xs font-medium text-white hover:bg-cyan-700"
              >
                <Check className="h-3 w-3" /> Allow
              </button>
              <button
                onClick={() => onSend("no", true)}
                className="flex items-center gap-1 rounded bg-slate-200 px-3 py-1.5 text-xs font-medium text-slate-700 hover:bg-slate-300 dark:bg-slate-700 dark:text-slate-200 dark:hover:bg-slate-600"
              >
                <X className="h-3 w-3" /> Deny
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default MessageBubble;
