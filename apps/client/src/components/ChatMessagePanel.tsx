import { RiUser3Line } from "@remixicon/react";
import MessageInput from "./MessageInput";

interface ChatMessagePanelProps {
  messages: any[];
  setMessages: (messages: any[]) => void;
}

const ChatMessagePanel = ({ messages, setMessages }: ChatMessagePanelProps) => {
  return (
    <div className="flex-1 flex flex-col">
      {/* Message Panel Area */}
      <div className="flex-1 overflow-y-auto p-6 bg-white">
        {messages.map((msg, idx) => (
          <div
            key={idx}
            className="flex gap-2 text-sm text-zinc-900 mb-2 bg-zinc-100 p-2 rounded-lg"
          >
            <RiUser3Line color="rgba(24,74,125,1)" />
            {msg.user}
          </div>
        ))}
      </div>

      {/* Message Input Bar */}
      <MessageInput messages={messages} setMessages={setMessages} />
    </div>
  );
};

export default ChatMessagePanel;
