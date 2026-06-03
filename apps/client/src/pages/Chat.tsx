import { useState } from "react";
import ChatSidebar from "../components/ChatSidebar";
import ChatEmptyState from "../components/ChatEmptyState";
import ChatHeader from "../components/ChatHeader";
import ChatMessagePanel from "../components/ChatMessagePanel";

const Chat = () => {
  const [messages, setMessages] = useState([]);
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);

  const handleToggleSidebar = () => setIsSidebarOpen((prev) => !prev);

  return (
    <div className="w-full h-screen bg-white text-zinc-950 flex overflow-hidden font-sans">
      <ChatSidebar
        isSidebarOpen={isSidebarOpen}
        onToggleSidebar={handleToggleSidebar}
      />

      {/* Main Chat Area */}
      <div className="flex flex-col bg-white flex-1">
        {messages.length === 0 && (
          <ChatEmptyState messages={messages} setMessages={setMessages} />
        )}

        {messages.length !== 0 && (
          <div className="flex-1 flex flex-col">
            <ChatHeader />
            <ChatMessagePanel messages={messages} setMessages={setMessages} />
          </div>
        )}
      </div>
    </div>
  );
};

export default Chat;
