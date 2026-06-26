import { Bot, User, BarChart2, FileVideo, FileAudio, FileSpreadsheet } from "lucide-react";
import ReactMarkdown from "react-markdown";
import type { ChatMessage, AnalystMessage } from "../types";

interface MessageBubbleProps {
  message: ChatMessage | AnalystMessage;
  isAnalystMode?: boolean;
  onSend?: (content: string, isApproval?: boolean) => Promise<void>;
  isLast?: boolean;
}

const MessageBubble = ({
  message,
  isAnalystMode = false,
  onSend,
  isLast = false,
}: MessageBubbleProps) => {
  const isUser = message.role === "user";
  const isSystem = message.role === "system";

  // System messages (Analyst mode dataset uploads)
  if (isSystem) {
    return (
      <div className="flex justify-center">
        <div className="flex items-center gap-2 rounded-xl border border-violet-800/50 bg-violet-900/20 px-3 py-1.5 text-xs text-violet-300">
          <FileSpreadsheet className="h-3.5 w-3.5 shrink-0" />
          <span>{message.mediaAttachment?.name ?? message.content}</span>
          <span className="text-violet-500">— uploaded ✓</span>
        </div>
      </div>
    );
  }

  // Type casting for analyst specific fields
  const analystMessage = message as AnalystMessage;
  const hasVisualizations =
    analystMessage.visualizations && analystMessage.visualizations.length > 0;

  return (
    <div className={`flex gap-3 ${isUser ? "justify-end" : "justify-start"}`}>
      {!isUser && (
        <div
          className={`mt-1 flex h-9 w-9 shrink-0 items-center justify-center rounded-xl text-white ${
            isAnalystMode
              ? "bg-violet-700"
              : "bg-slate-950 dark:bg-slate-700"
          }`}
        >
          {isAnalystMode ? (
            <BarChart2 className="h-4 w-4" />
          ) : (
            <Bot className="h-4 w-4" />
          )}
        </div>
      )}

      <div className={`flex flex-col gap-3 max-w-[78%]`}>
        {/* Media Attachments for User (Regular Chat) */}
        {!isAnalystMode && message.mediaAttachment && (
          <div className="flex items-center gap-1.5 self-end rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-100 dark:bg-slate-800 px-2.5 py-1 text-xs text-slate-600 dark:text-slate-300">
            {message.mediaAttachment.type === "video" ? (
              <FileVideo className="h-3.5 w-3.5" />
            ) : (
              <FileAudio className="h-3.5 w-3.5" />
            )}
            <span className="max-w-[160px] truncate">
              {message.mediaAttachment.name}
            </span>
          </div>
        )}

        {/* Text content bubble */}
        {(message.content || message.pending) && (
          <div
            className={`rounded-2xl px-4 py-3 text-sm leading-6 shadow-sm ${
              isUser
                ? isAnalystMode
                  ? "bg-violet-700 text-white"
                  : "bg-cyan-600 dark:bg-cyan-700 text-white"
                : isAnalystMode
                  ? "border border-slate-700 bg-slate-800 text-slate-100"
                  : "border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-800 dark:text-slate-100"
            } ${message.pending && !hasVisualizations ? "animate-pulse opacity-70" : ""}`}
          >
            {isUser || !isAnalystMode ? (
              <span className="whitespace-pre-wrap">
                {message.content || (message.pending ? (isAnalystMode ? "Analysing…" : "Thinking…") : "")}
              </span>
            ) : (
              <div className="prose prose-sm prose-invert max-w-none">
                <ReactMarkdown>{message.content || (message.pending ? "Analysing…" : "")}</ReactMarkdown>
              </div>
            )}

            {/* Approval Buttons (Regular Chat) */}
            {!isAnalystMode && (message as ChatMessage).requires_approval && isLast && onSend && (
              <div className="mt-3 flex gap-2">
                <button
                  onClick={() => onSend("yes", true)}
                  className="px-3 py-1.5 bg-cyan-600 text-white rounded-lg hover:bg-cyan-700 transition text-xs font-medium"
                >
                  ✓ Yes, go ahead
                </button>
                <button
                  onClick={() => onSend("no", true)}
                  className="px-3 py-1.5 bg-slate-200 dark:bg-slate-700 text-slate-800 dark:text-slate-200 rounded-lg hover:bg-slate-300 dark:hover:bg-slate-600 transition text-xs font-medium"
                >
                  ✕ No, skip it
                </button>
              </div>
            )}
          </div>
        )}

        {/* Visualization cards (Analyst Mode) */}
        {isAnalystMode && hasVisualizations &&
          analystMessage.visualizations!.map((vis, idx) => (
            <div
              key={idx}
              className="rounded-2xl border border-violet-500/30 bg-slate-800/80 shadow-lg overflow-hidden"
            >
              <div className="flex items-center gap-2 px-4 py-3 border-b border-slate-700/60 bg-slate-900/60">
                <BarChart2 className="h-4 w-4 text-violet-400 shrink-0" />
                <span className="text-sm font-semibold text-violet-200 truncate">
                  {vis.title}
                </span>
                <span className="ml-auto text-xs text-slate-500 uppercase tracking-wide font-mono shrink-0">
                  {vis.chart_type}
                </span>
              </div>
              <div className="bg-white/5 p-2">
                <img
                  src={`data:image/png;base64,${vis.image}`}
                  alt={vis.title}
                  className="w-full rounded-lg object-contain"
                  style={{ maxHeight: "420px" }}
                />
              </div>
              {vis.summary && (
                <div className="px-4 py-3 border-t border-slate-700/60">
                  <p className="text-xs text-slate-400 leading-5">{vis.summary}</p>
                </div>
              )}
            </div>
          ))}

        {/* Loading skeleton for visualization when pending */}
        {isAnalystMode && message.pending && !hasVisualizations && !message.content && (
          <div className="rounded-2xl border border-slate-700 bg-slate-800/80 px-4 py-3 animate-pulse">
            <span className="text-sm text-slate-500">Analysing…</span>
          </div>
        )}
      </div>

      {isUser && (
        <div
          className={`mt-1 flex h-9 w-9 shrink-0 items-center justify-center rounded-xl ${
            isAnalystMode
              ? "bg-violet-900/60 text-violet-300"
              : "bg-cyan-100 dark:bg-cyan-900/60 text-cyan-800 dark:text-cyan-300"
          }`}
        >
          <User className="h-4 w-4" />
        </div>
      )}
    </div>
  );
};

export default MessageBubble;
