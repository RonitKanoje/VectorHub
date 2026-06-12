import { useCallback, useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import toast from "react-hot-toast";
import { useDispatch } from "react-redux";
import ChatSidebar from "../components/ChatSidebar";
import ChatHeader from "../components/ChatHeader";
import ChatMessagePanel from "../components/ChatMessagePanel";
import type { MediaPayload } from "../components/MessageInput";
import api from "../services/api";
import { logout as clearAuth } from "../redux/features/authSlice";
import type { AppDispatch } from "../redux/store";
import { useThreads } from "../hooks/useThreads";
import { useConversation } from "../hooks/useConversation";
import { useMediaProcessing } from "../hooks/useMediaProcessing";

const Chat = () => {
  const [activeThreadId, setActiveThreadId] = useState<string | null>(null);
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const dispatch = useDispatch<AppDispatch>();
  const navigate = useNavigate();

  // Hooks
  const {
    threads,
    isLoadingThreads,
    draftThreadIds,
    loadThreads,
    handleNewChat,
    ensureActiveThread,
    removeDraftThread,
    setThreads,
  } = useThreads();

  const {
    messages,
    activeStatus,
    isLoadingConversation,
    isSending,
    setMessages,
    setActiveStatus,
    loadConversation,
    handleSend,
  } = useConversation();

  const { isProcessing, handleProcessMedia } = useMediaProcessing();

  // Derived state
  const activeTitle = useMemo(
    () =>
      threads.find((t) => t.thread_id === activeThreadId)?.title ?? "New Chat",
    [activeThreadId, threads],
  );

  const inputDisabled = isLoadingConversation;

  // Effects

  // Load threads once on mount
  useEffect(() => {
    const id = window.setTimeout(() => void loadThreads(), 0);
    return () => window.clearTimeout(id);
  }, [loadThreads]);

  // Load conversation whenever the active thread changes
  useEffect(() => {
    if (!activeThreadId) return;
    const isDraft = draftThreadIds.has(activeThreadId);
    const id = window.setTimeout(
      () => void loadConversation(activeThreadId, isDraft),
      0,
    );
    return () => window.clearTimeout(id);
  }, [activeThreadId, draftThreadIds, loadConversation]);

  // Handlers

  const handleToggleSidebar = () => setIsSidebarOpen((prev) => !prev);

  const handleNewChatClick = () =>
    handleNewChat(setActiveThreadId, setActiveStatus, setMessages);

  const getEnsuredThread = useCallback(
    () => ensureActiveThread(activeThreadId, setActiveThreadId),
    [activeThreadId, ensureActiveThread],
  );

  const handleSendMessage = async (content: string) => {
    await handleSend(
      content,
      activeThreadId,
      getEnsuredThread,
      removeDraftThread,
      setThreads,
    );
  };

  const handleProcessMediaClick = async (payload: MediaPayload) => {
    await handleProcessMedia(
      payload,
      getEnsuredThread,
      removeDraftThread,
      setActiveStatus,
      loadThreads,
    );
  };

  const handleLogout = async () => {
    try {
      await api.get("/api/auth/logout");
      toast.success("Logged out");
    } catch {
      toast.error("Session cleared locally");
    } finally {
      dispatch(clearAuth());
      navigate("/", { replace: true });
    }
  };

  const handleLogoutAll = async () => {
    try {
      await api.get("/api/auth/logoutAll");
      toast.success("Logged out from every device");
    } catch {
      toast.error("Could not reach logout-all endpoint");
    } finally {
      dispatch(clearAuth());
      navigate("/", { replace: true });
    }
  };

  // Render
  return (
    <div className="flex h-screen w-full overflow-hidden bg-slate-100 text-slate-950">
      <ChatSidebar
        isSidebarOpen={isSidebarOpen}
        onToggleSidebar={handleToggleSidebar}
        threads={threads}
        activeThreadId={activeThreadId}
        isLoadingThreads={isLoadingThreads}
        onNewChat={handleNewChatClick}
        onSelectThread={setActiveThreadId}
        onLogout={() => void handleLogout()}
        onLogoutAll={() => void handleLogoutAll()}
      />

      <div className="flex min-w-0 flex-1 flex-col bg-white">
        <ChatHeader
          title={activeTitle}
          status={isProcessing ? (activeStatus ?? "processing") : activeStatus}
        />
        <ChatMessagePanel
          messages={messages}
          disabled={inputDisabled}
          isSending={isSending}
          onSend={handleSendMessage}
          onProcessMedia={handleProcessMediaClick}
        />
      </div>
    </div>
  );
};

export default Chat;
