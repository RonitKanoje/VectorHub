import { Bot, User, BarChart2 } from "lucide-react";
import ReactMarkdown from "react-markdown";
import type { AnalystChatMessage as AnalystChatMessageType } from "../types/analyst";

interface AnalystChatMessageProps {
  message: AnalystChatMessageType;
}

const AnalystChatMessage = ({ message }: AnalystChatMessageProps) => {
  const isUser = message.role === "user";
  const hasVisualizations =
    message.visualizations && message.visualizations.length > 0;

  return (
    <div className={`flex gap-3 ${isUser ? "justify-end" : "justify-start"}`}>
      {!isUser && (
        <div className="mt-1 flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-violet-700 text-white">
          <Bot className="h-4 w-4" />
        </div>
      )}

      <div className={`flex flex-col gap-3 max-w-[78%]`}>
        {/* Text content bubble */}
        {(message.content || message.pending) && (
          <div
            className={`rounded-2xl px-4 py-3 text-sm leading-6 shadow-sm ${
              isUser
                ? "bg-violet-700 text-white"
                : "border border-slate-700 bg-slate-800 text-slate-100"
            } ${message.pending && !hasVisualizations ? "animate-pulse opacity-70" : ""}`}
          >
            {isUser ? (
              <span className="whitespace-pre-wrap">
                {message.content || (message.pending ? "Analysing…" : "")}
              </span>
            ) : (
              <div className="prose prose-sm prose-invert max-w-none">
                <ReactMarkdown>{message.content || (message.pending ? "Analysing…" : "")}</ReactMarkdown>
              </div>
            )}
          </div>
        )}

        {/* Visualization cards */}
        {hasVisualizations &&
          message.visualizations!.map((vis, idx) => (
            <div
              key={idx}
              className="rounded-2xl border border-violet-500/30 bg-slate-800/80 shadow-lg overflow-hidden"
            >
              {/* Chart header */}
              <div className="flex items-center gap-2 px-4 py-3 border-b border-slate-700/60 bg-slate-900/60">
                <BarChart2 className="h-4 w-4 text-violet-400 shrink-0" />
                <span className="text-sm font-semibold text-violet-200 truncate">
                  {vis.title}
                </span>
                <span className="ml-auto text-xs text-slate-500 uppercase tracking-wide font-mono shrink-0">
                  {vis.chart_type}
                </span>
              </div>

              {/* Chart image */}
              <div className="bg-white/5 p-2">
                <img
                  src={`data:image/png;base64,${vis.image}`}
                  alt={vis.title}
                  className="w-full rounded-lg object-contain"
                  style={{ maxHeight: "420px" }}
                />
              </div>

              {/* Optional summary */}
              {vis.summary && (
                <div className="px-4 py-3 border-t border-slate-700/60">
                  <p className="text-xs text-slate-400 leading-5">{vis.summary}</p>
                </div>
              )}
            </div>
          ))}

        {/* Loading skeleton for visualization when pending */}
        {message.pending && !hasVisualizations && !message.content && (
          <div className="rounded-2xl border border-slate-700 bg-slate-800/80 px-4 py-3 animate-pulse">
            <span className="text-sm text-slate-500">Analysing…</span>
          </div>
        )}
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