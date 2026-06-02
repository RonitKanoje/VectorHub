import {
  RiArrowDropLeftLine,
  RiArrowDropRightLine,
  RiUser3Line,
} from "@remixicon/react";
import { useState } from "react";
import MessageInput from "../components/MessageInput";

const Chat = () => {
  const [messages, setMessages] = useState([]);
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);

  return (
    <div className="w-full h-screen bg-white text-zinc-950 flex overflow-hidden font-sans">
      {/* Sidebar */}
      {isSidebarOpen && (
        <div className="w-64 bg-zinc-50 border-r border-zinc-200 flex flex-col p-4 relative">
          <button
            className="absolute top-4 right-4 text-zinc-500 hover:text-zinc-700 cursor-pointer"
            onClick={() => setIsSidebarOpen((prev) => !prev)}
          >
            <RiArrowDropLeftLine />
          </button>
          <h1 className="text-sm font-semibold text-zinc-500 uppercase tracking-wider px-2 mb-4">
            Chats
          </h1>

          <div className="mb-6">
            <button className="w-full bg-zinc-900 hover:bg-zinc-800 text-white text-sm font-medium py-2 px-4 rounded-xl transition-all active:scale-[0.98] cursor-pointer">
              New Chat
            </button>
          </div>

          <h2 className="text-xs font-semibold text-zinc-400 uppercase tracking-wider px-2 mb-2">
            Chat History
          </h2>

          {/* Chat history list */}
          <div className="flex-1 overflow-y-auto space-y-1">
            <div className="px-3 py-2 rounded-lg text-sm text-zinc-600 hover:bg-zinc-200/60 hover:text-zinc-900 cursor-pointer transition-colors">
              Previous Chat 1
            </div>
          </div>
        </div>
      )}

      {!isSidebarOpen && (
        <div className="w-10 relative">
          <button
            className="absolute top-4 left-4 text-zinc-500 hover:text-zinc-700 z-10 cursor-pointer"
            onClick={() => setIsSidebarOpen((prev) => !prev)}
          >
            <RiArrowDropRightLine />
          </button>
        </div>
      )}

      {/* Main Chat Area */}
      <div className="flex flex-col bg-white flex-1">
        {messages.length === 0 && (
          <div className="w-full flex-1 flex flex-col items-center justify-center">
            <h1 className="text-2xl font-bold text-zinc-800 mb-6 text-center">
              Welcome to VectorHub!
            </h1>

            <div className="w-full max-w-3xl px-4">
              <MessageInput messages={messages} setMessages={setMessages} />
            </div>
          </div>
        )}

        {messages.length !== 0 && (
          <div className="flex-1 flex flex-col">
            {/* Top Header */}
            <div className="h-14 border-b border-zinc-200 flex items-center px-6">
              <h2 className="text-sm font-semibold text-zinc-800">VectorHub</h2>
            </div>

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
        )}
      </div>
    </div>
  );
};

export default Chat;
