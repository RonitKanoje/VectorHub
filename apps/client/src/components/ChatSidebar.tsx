import { RiArrowDropLeftLine, RiArrowDropRightLine } from "@remixicon/react";

interface ChatSidebarProps {
  isSidebarOpen: boolean;
  onToggleSidebar: () => void;
}

const ChatSidebar = ({ isSidebarOpen, onToggleSidebar }: ChatSidebarProps) => {
  if (isSidebarOpen) {
    return (
      <div className="w-64 bg-zinc-50 border-r border-zinc-200 flex flex-col p-4 relative">
        <button
          className="absolute top-4 right-4 text-zinc-500 hover:text-zinc-700 cursor-pointer"
          onClick={onToggleSidebar}
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
    );
  }

  return (
    <div className="w-10 relative">
      <button
        className="absolute top-4 left-4 text-zinc-500 hover:text-zinc-700 z-10 cursor-pointer"
        onClick={onToggleSidebar}
      >
        <RiArrowDropRightLine />
      </button>
    </div>
  );
};

export default ChatSidebar;
