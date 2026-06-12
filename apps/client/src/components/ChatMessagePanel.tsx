import { Bot, Sparkles, User } from "lucide-react";
import { useEffect, useRef } from "react";
import MessageInput from "./MessageInput";
import type { MediaPayload } from "./MessageInput";

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  pending?: boolean;
}

interface ChatMessagePanelProps {
  messages: ChatMessage[];
  disabled?: boolean;
  isSending?: boolean;
  onSend: (content: string) => Promise<void>; // it will accept content as a argument and function must return Promise 
  onProcessMedia: (payload: MediaPayload) => Promise<void>;
}

const ChatMessagePanel = ({
  messages,
  disabled = false,
  isSending = false,
  onSend,
  onProcessMedia,
}: ChatMessagePanelProps) => {
  const scrollRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    scrollRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]); // scroll till new message on changing the messages 

  return (
    <div className="flex min-h-0 flex-1 flex-col">
      <div className="flex-1 overflow-y-auto bg-[radial-gradient(circle_at_top_left,#e0f7ff_0,transparent_30%),linear-gradient(180deg,#f8fafc_0%,#eef4f8_100%)] px-4 py-6">
        {messages.length === 0 && (
          <div className="mx-auto flex h-full max-w-3xl flex-col items-center justify-center text-center">
            <div className="mb-5 flex h-14 w-14 items-center justify-center rounded-2xl bg-cyan-100 text-cyan-700">
              <Sparkles className="h-7 w-7" />
            </div>
            <h1 className="text-3xl font-bold tracking-tight text-slate-950">
              Ask normally, or add content for RAG.
            </h1>
            <p className="mt-3 max-w-xl text-sm leading-6 text-slate-600">
              General questions work immediately. Use the plus button when you want this chat to answer from YouTube, audio, video, or text chunks.
            </p>
          </div>
        )}

        <div className="mx-auto flex max-w-4xl flex-col gap-4">
          {messages.map((message, idx) => {
            const isUser = message.role === "user";

            return (
              <div
                key={`${message.role}-${idx}-${message.content.slice(0, 12)}`}
                className={`flex gap-3 ${isUser ? "justify-end" : "justify-start"}`}
              >
                {!isUser && (
                  <div className="mt-1 flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-slate-950 text-white">
                    <Bot className="h-4 w-4" />
                  </div>
                )}

                <div
                  className={`max-w-[78%] rounded-2xl px-4 py-3 text-sm leading-6 shadow-sm ${
                    isUser
                      ? "bg-cyan-700 text-white"
                      : "border border-slate-200 bg-white text-slate-800"
                  } ${message.pending ? "animate-pulse" : ""}`}
                >
                  {message.content}
                </div>

                {isUser && (
                  <div className="mt-1 flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-cyan-100 text-cyan-800">
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
        onSend={onSend}
        onProcessMedia={onProcessMedia}
      />
    </div>
  );
};

export default ChatMessagePanel;
