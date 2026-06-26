import {
  Bot,
  BarChart2,
  Sparkles,
  User,
  FileVideo,
  FileAudio,
} from "lucide-react";
import { useEffect, useRef } from "react";
import MessageInput from "./MessageInput";
import type { MediaPayload, UploadedItem } from "../types";
import type { ChatMessage } from "../types";

interface ChatMessagePanelProps {
  messages: ChatMessage[];
  disabled?: boolean;
  isSending?: boolean;
  isAnalystMode?: boolean;
  uploadedItems?: UploadedItem[];
  onSend: (content: string, isApproval?: boolean) => Promise<void>;
  onProcessMedia: (payload: MediaPayload) => Promise<void>;
  onRemoveUpload?: (index: number) => void;
}

const ChatMessagePanel = ({
  messages,
  disabled = false,
  isSending = false,
  isAnalystMode = false,
  // uploadedItems = [],
  onSend,
  onProcessMedia,
  // onRemoveUpload,
}: ChatMessagePanelProps) => {
  const scrollRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    scrollRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  return (
    <div className="flex min-h-0 flex-1 flex-col">
      <div className="flex-1 overflow-y-auto bg-white dark:bg-slate-950 px-4 py-6">
        {messages.length === 0 && (
          <div className="mx-auto flex h-full max-w-3xl flex-col items-center justify-center text-center py-16">
            <div
              className={`mb-5 flex h-14 w-14 items-center justify-center rounded-2xl ${
                isAnalystMode
                  ? "bg-violet-100 dark:bg-violet-900/40 text-violet-700 dark:text-violet-300"
                  : "bg-cyan-100 dark:bg-cyan-900/40 text-cyan-700 dark:text-cyan-300"
              }`}
            >
              {isAnalystMode ? (
                <BarChart2 className="h-7 w-7" />
              ) : (
                <Sparkles className="h-7 w-7" />
              )}
            </div>
            <h1 className="text-3xl font-bold tracking-tight text-slate-950 dark:text-white">
              {isAnalystMode
                ? "Analyst Mode"
                : "Ask normally, or add content for RAG."}
            </h1>
            <p className="mt-3 max-w-xl text-sm leading-6 text-slate-500 dark:text-slate-400">
              {isAnalystMode
                ? "Upload a CSV or Excel file, then ask questions about your data. Charts and summaries are generated automatically."
                : "General questions work immediately. Use the plus button when you want this chat to answer from YouTube, audio, video, or text chunks."}
            </p>
          </div>
        )}

        <div className="mx-auto flex max-w-4xl flex-col gap-4">
          {messages.map((message, idx) => {
            const isUser = message.role === "user";
            const messageKey = message.id ?? `msg-${idx}`; // safe fallback

            return (
              <div
                key={messageKey} // stable key with fallback
                className={`flex gap-3 ${isUser ? "justify-end" : "justify-start"}`}
              >
                {!isUser && (
                  <div
                    className={`mt-1 flex h-9 w-9 shrink-0 items-center justify-center rounded-xl text-white ${
                      isAnalystMode
                        ? "bg-violet-600 dark:bg-violet-700"
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

                <div className="flex flex-col gap-1 max-w-[78%]">
                  {message.mediaAttachment && (
                    <div
                      key={`media-${messageKey}`} // key on media pill
                      className="flex items-center gap-1.5 self-end rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-100 dark:bg-slate-800 px-2.5 py-1 text-xs text-slate-600 dark:text-slate-300"
                    >
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

                  <div
                    className={`rounded-2xl px-4 py-3 text-sm leading-6 shadow-sm ${
                      isUser
                        ? "bg-cyan-600 dark:bg-cyan-700 text-white"
                        : "border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-800 dark:text-slate-100"
                    } ${message.pending ? "animate-pulse opacity-70" : ""}`}
                  >
                    <span className="whitespace-pre-wrap">
                      {message.content || (message.pending ? "Thinking…" : "")}
                    </span>

                    {message.requires_approval &&
                      idx === messages.length - 1 && (
                        <div className="mt-3 flex gap-2">
                          <button
                            key={`approve-yes-${messageKey}`} //key on button
                            onClick={() => onSend("yes", true)}
                            className="px-3 py-1.5 bg-cyan-600 text-white rounded-lg hover:bg-cyan-700 transition text-xs font-medium"
                          >
                            ✓ Yes, go ahead
                          </button>
                          <button
                            key={`approve-no-${messageKey}`} //key on button
                            onClick={() => onSend("no", true)}
                            className="px-3 py-1.5 bg-slate-200 dark:bg-slate-700 text-slate-800 dark:text-slate-200 rounded-lg hover:bg-slate-300 dark:hover:bg-slate-600 transition text-xs font-medium"
                          >
                            ✕ No, skip it
                          </button>
                        </div>
                      )}
                  </div>
                </div>

                {isUser && (
                  <div className="mt-1 flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-cyan-100 dark:bg-cyan-900/60 text-cyan-800 dark:text-cyan-300">
                    <User className="h-4 w-4" />
                  </div>
                )}
              </div>
            );
          })}
          <div ref={scrollRef} />
        </div>
      </div>

      <MessageInput
        disabled={disabled}
        isSending={isSending}
        isAnalystMode={isAnalystMode}
        // uploadedItems={uploadedItems}
        onSend={onSend}
        onProcessMedia={onProcessMedia}
        // onRemoveUpload={onRemoveUpload}
      />
    </div>
  );
};

export default ChatMessagePanel;
