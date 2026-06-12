import {
  LogOut,
  MessageSquare,
  MonitorX,
  PanelLeftClose,
  PanelLeftOpen,
  Plus,
  Settings,
} from "lucide-react";
import { useState } from "react";

export interface ChatThread {
  thread_id: string;
  title: string;
}

interface ChatSidebarProps {
  isSidebarOpen: boolean;
  onToggleSidebar: () => void;
  threads: ChatThread[];
  activeThreadId: string | null;
  isLoadingThreads: boolean;
  onNewChat: () => void;
  onSelectThread: (threadId: string) => void;
  onLogout: () => void;
  onLogoutAll: () => void;
}

const ChatSidebar = ({
  isSidebarOpen,
  onToggleSidebar,
  threads,
  activeThreadId,
  isLoadingThreads,
  onNewChat,
  onSelectThread,
  onLogout,
  onLogoutAll,
}: ChatSidebarProps) => {
  const [showSettings, setShowSettings] = useState(false);

  if (isSidebarOpen) {
    return (
      // aside => since we are working on sidebar
      <aside className="relative flex w-72   shrink-0 flex-col border-r border-slate-200 bg-slate-950 p-4 text-white">
        <button
          type="button"
          className="absolute right-4 top-4 flex h-8 w-8 items-center justify-center rounded-lg text-slate-400 transition hover:bg-white/10 hover:text-white"
          onClick={onToggleSidebar}
          aria-label="Collapse sidebar"
        >
          <PanelLeftClose className="h-4 w-4" />
        </button>

        <div className="mb-6 pr-10">
          <h1 className="text-lg font-bold tracking-tight">VectorHub</h1>
          <p className="text-xs text-slate-400">Your processed chats</p>
        </div>

        <button
          type="button"
          className="mb-5 flex h-11 w-full items-center justify-center gap-2 rounded-xl bg-cyan-500 text-sm font-semibold text-slate-950 transition hover:bg-cyan-400 active:scale-[0.98]"
          onClick={onNewChat}
        >
          <Plus className="h-4 w-4" />
          New Chat
        </button>

        <h2 className="mb-2 px-2 text-xs font-semibold uppercase tracking-wider text-slate-500">
          Chat History
        </h2>

        <div className="min-h-0 flex-1 overflow-y-auto space-y-1 pr-1">
          {isLoadingThreads && (
            <div className="px-3 py-2 text-sm text-slate-400">
              Loading chats...
            </div>
          )}

          {!isLoadingThreads && threads.length === 0 && (
            <div className="rounded-xl border border-white/10 bg-white/5 px-3 py-3 text-sm text-slate-400">
              Upload content to create your first chat.
            </div>
          )}

          {threads.map((thread) => {
            const isActive = thread.thread_id === activeThreadId;

            return (
              <button
                key={thread.thread_id}
                type="button"
                className={`flex w-full items-start gap-3 rounded-xl px-3 py-2.5 text-left text-sm transition ${
                  isActive
                    ? "bg-white text-slate-950"
                    : "text-slate-300 hover:bg-white/10 hover:text-white"
                }`}
                onClick={() => onSelectThread(thread.thread_id)}
              >
                <MessageSquare className="mt-0.5 h-4 w-4 shrink-0" />
                <span className="line-clamp-2">
                  {thread.title || "New Chat"}
                </span>
              </button>
            );
          })}
        </div>

        <div className="relative mt-4 border-t border-white/10 pt-4">
          {showSettings && (
            <div className="absolute bottom-16 left-0 right-0 rounded-2xl border border-white/10 bg-slate-900 p-2 shadow-2xl">
              <button
                type="button"
                className="flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-left text-sm text-slate-200 transition hover:bg-white/10"
                onClick={onLogout}
              >
                <LogOut className="h-4 w-4" />
                Logout
              </button>
              <button
                type="button"
                className="flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-left text-sm text-red-200 transition hover:bg-red-500/10"
                onClick={onLogoutAll}
              >
                <MonitorX className="h-4 w-4" />
                Logout all devices
              </button>
            </div>
          )}

          <button
            type="button"
            className="flex h-11 w-full items-center justify-center gap-2 rounded-xl border border-white/10 bg-white/5 text-sm font-medium text-slate-200 transition hover:bg-white/10"
            onClick={() => setShowSettings((prev) => !prev)}
          >
            <Settings className="h-4 w-4" />
            Settings
          </button>
        </div>
      </aside>
    );
  }

  return (
    <aside className="relative w-14 shrink-0 border-r border-slate-200 bg-white">
      <button
        type="button"
        className="absolute left-3 top-4 flex h-9 w-9 items-center justify-center rounded-xl text-slate-600 transition hover:bg-slate-100 hover:text-slate-950"
        onClick={onToggleSidebar}
        aria-label="Open sidebar"
      >
        <PanelLeftOpen className="h-4 w-4" />
      </button>
    </aside>
  );
};

export default ChatSidebar;
