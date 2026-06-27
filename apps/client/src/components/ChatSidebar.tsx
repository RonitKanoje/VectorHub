import {
  BarChart2,
  LogOut,
  MessageSquare,
  MonitorX,
  PanelLeftClose,
  PanelLeftOpen,
  Plus,
  Settings,
} from "lucide-react";
import { useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import type { Thread } from "../types";

interface ChatSidebarProps {
  isSidebarOpen: boolean;
  onToggleSidebar: () => void;
  threads: Thread[];
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
  const navigate = useNavigate();
  const location = useLocation();
  const isOnAnalyst = location.pathname === "/analyst";

  if (isSidebarOpen) {
    return (
      <aside className="relative flex w-72 shrink-0 flex-col border-r border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-950 p-4 text-slate-950 dark:text-white">
        <button
          type="button"
          className="absolute right-4 top-4 flex h-8 w-8 items-center justify-center rounded-lg text-slate-500 dark:text-slate-400 transition hover:bg-slate-100 dark:hover:bg-white/10 hover:text-slate-950 dark:hover:text-white"
          onClick={onToggleSidebar}
          aria-label="Collapse sidebar"
        >
          <PanelLeftClose className="h-4 w-4" />
        </button>

        <div className="mb-5 pr-10">
          <h1 className="text-lg font-bold tracking-tight text-slate-950 dark:text-white">
            VectorHub
          </h1>
          <p className="text-xs text-slate-500 dark:text-slate-400">
            Your intelligent assistant
          </p>
        </div>

        <button
          type="button"
          className="mb-3 flex h-11 w-full items-center justify-center gap-2 rounded-xl bg-black text-white hover:bg-slate-800 dark:bg-cyan-500 dark:text-slate-950 dark:hover:bg-cyan-400 text-sm font-semibold transition active:scale-[0.98]"
          onClick={onNewChat}
        >
          <Plus className="h-4 w-4" />
          New Chat
        </button>

        <button
          type="button"
          onClick={() => navigate(isOnAnalyst ? "/chat" : "/analyst")}
          className={`mb-5 flex h-11 w-full items-center justify-center gap-2 rounded-xl border text-sm font-semibold transition active:scale-[0.98] ${
            isOnAnalyst
              ? "border-violet-500 bg-violet-600 text-white hover:bg-violet-500"
              : "border-slate-200 text-slate-700 hover:bg-slate-100 dark:border-slate-700 dark:text-slate-300 dark:hover:bg-white/10"
          }`}
        >
          <BarChart2 className="h-4 w-4" />
          {isOnAnalyst ? "← Back to Chat" : "Analyst Mode"}
        </button>

        <h2 className="mb-2 px-2 text-xs font-semibold uppercase tracking-wider text-slate-400 dark:text-slate-500">
          Chat History
        </h2>

        <div
          className="min-h-0 flex-1 space-y-1 overflow-y-auto pr-1"
          style={{ scrollbarWidth: "none", msOverflowStyle: "none" }}
        >
          {isLoadingThreads && (
            <div className="px-3 py-2 text-sm text-slate-500 dark:text-slate-400">
              Loading chats...
            </div>
          )}

          {!isLoadingThreads && threads.length === 0 && (
            <div className="rounded-xl border border-slate-200 bg-slate-50 px-3 py-3 text-sm text-slate-500 dark:border-white/10 dark:bg-white/5 dark:text-slate-400">
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
                    ? "border border-slate-200 bg-slate-100 text-slate-950 dark:border-white/10 dark:bg-white/10 dark:text-white"
                    : "text-slate-600 hover:bg-slate-100 hover:text-slate-950 dark:text-slate-400 dark:hover:bg-white/10 dark:hover:text-white"
                }`}
                onClick={() => onSelectThread(thread.thread_id)}
              >
                <MessageSquare className="mt-0.5 h-4 w-4 shrink-0" />
                <span className="line-clamp-2">{thread.title || "New Chat"}</span>
              </button>
            );
          })}
        </div>

        <div className="relative mt-4 border-t border-slate-200 pt-4 dark:border-white/10">
          {showSettings && (
            <div className="absolute bottom-16 left-0 right-0 z-10 rounded-2xl border border-slate-200 bg-white p-2 shadow-2xl dark:border-white/10 dark:bg-slate-900">
              <button
                type="button"
                className="flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-left text-sm text-slate-700 transition hover:bg-slate-100 dark:text-slate-200 dark:hover:bg-white/10"
                onClick={onLogout}
              >
                <LogOut className="h-4 w-4" />
                Logout
              </button>
              <button
                type="button"
                className="flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-left text-sm text-red-600 transition hover:bg-red-50 dark:text-red-300 dark:hover:bg-red-500/10"
                onClick={onLogoutAll}
              >
                <MonitorX className="h-4 w-4" />
                Logout all devices
              </button>
            </div>
          )}

          <button
            type="button"
            className="flex h-11 w-full items-center justify-center gap-2 rounded-xl border border-slate-200 bg-slate-50 text-sm font-medium text-slate-700 transition hover:bg-slate-100 dark:border-white/10 dark:bg-white/5 dark:text-slate-200 dark:hover:bg-white/10"
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
    <aside className="relative w-14 shrink-0 border-r border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-950">
      <button
        type="button"
        className="absolute left-3 top-4 flex h-9 w-9 items-center justify-center rounded-xl text-slate-600 transition hover:bg-slate-100 hover:text-slate-950 dark:text-slate-400 dark:hover:bg-slate-800 dark:hover:text-white"
        onClick={onToggleSidebar}
        aria-label="Open sidebar"
      >
        <PanelLeftOpen className="h-4 w-4" />
      </button>
    </aside>
  );
};

export default ChatSidebar;
