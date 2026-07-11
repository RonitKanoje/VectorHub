import ReactMarkdown from "react-markdown";
import {
  FileText,
  Video,
  Mic,
  FileBarChart,
  Link,
  Play,
  ShieldQuestion,
} from "lucide-react";
import type { ChatMessage, AnalystMessage } from "../types";

interface MessageBubbleProps {
  message: ChatMessage | AnalystMessage;
  isAnalystMode?: boolean;
  onApprove?: (answer: "yes" | "no") => void;
}

const MessageBubble = ({
  message,
  isAnalystMode,
  onApprove,
}: MessageBubbleProps) => {
  const isUser = message.role === "user";
  const isPending = "pending" in message && message.pending;

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
          <div className="mb-2 flex items-center gap-2 text-sm font-medium text-slate-600 dark:text-violet-400">
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

        {"requires_approval" in message &&
          message.requires_approval &&
          onApprove && (
            <div className="mt-4 rounded-xl border border-amber-200 dark:border-amber-700 bg-amber-50 dark:bg-amber-900/30 px-4 py-3">
              <div className="flex items-center gap-2 text-sm font-semibold text-amber-800 dark:text-amber-300 mb-3">
                <ShieldQuestion className="h-4 w-4 shrink-0" />
                <span>
                  The assistant wants to use{" "}
                  <code className="rounded bg-amber-100 dark:bg-amber-800 px-1.5 py-0.5 font-mono text-xs">
                    {message.tool}
                  </code>
                  . Allow?
                </span>
              </div>
              <div className="flex gap-2">
                <button
                  onClick={() => onApprove("yes")}
                  className="flex-1 rounded-lg bg-emerald-600 hover:bg-emerald-700 active:bg-emerald-800 text-white text-sm font-medium py-1.5 transition-colors"
                >
                  Yes, allow
                </button>
                <button
                  onClick={() => onApprove("no")}
                  className="flex-1 rounded-lg bg-slate-200 hover:bg-slate-300 dark:bg-slate-700 dark:hover:bg-slate-600 text-slate-800 dark:text-slate-200 text-sm font-medium py-1.5 transition-colors"
                >
                  No, cancel
                </button>
              </div>
            </div>
          )}

        {"mediaAttachment" in message && message.mediaAttachment && (
          <div className="mt-3 flex items-center gap-2 rounded-lg bg-black/10 px-3 py-2 text-sm">
            {getMediaIcon(message.mediaAttachment.type)}
            <span className="truncate">{message.mediaAttachment.name}</span>
          </div>
        )}

        {isAnalystMode &&
          "visualizations" in message &&
          message.visualizations &&
          message.visualizations.length > 0 && (
            <div className="mt-4 flex flex-col gap-4">
              {message.visualizations.map((visualization, index) => (
                <div
                  key={index}
                  className="overflow-hidden rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900"
                >
                  <div className="border-b border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 px-3 py-2">
                    <div className="text-sm font-semibold text-slate-700 dark:text-slate-200">
                      {visualization.title}
                    </div>

                    {visualization.summary && (
                      <div className="mt-1 text-xs text-slate-500 dark:text-slate-400">
                        {visualization.summary}
                      </div>
                    )}
                  </div>

                  <img
                    src={`data:image/png;base64,${visualization.image}`}
                    alt={visualization.title}
                    className="w-full h-auto object-contain p-2"
                  />
                </div>
              ))}
            </div>
          )}
      </div>
    </div>
  );
};

export default MessageBubble;
