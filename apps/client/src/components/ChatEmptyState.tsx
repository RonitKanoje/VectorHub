import MessageInput from "./MessageInput";

interface ChatEmptyStateProps {
  messages: any[];
  setMessages: (messages: any[]) => void;
}

const ChatEmptyState = ({ messages, setMessages }: ChatEmptyStateProps) => {
  return (
    <div className="w-full flex-1 flex flex-col items-center justify-center">
      <h1 className="text-2xl font-bold text-zinc-800 mb-6 text-center">
        Welcome to VectorHub!
      </h1>

      <div className="w-full max-w-3xl px-4">
        <MessageInput messages={messages} setMessages={setMessages} />
      </div>
    </div>
  );
};

export default ChatEmptyState;
