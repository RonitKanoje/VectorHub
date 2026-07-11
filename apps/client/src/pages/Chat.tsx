import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import toast from "react-hot-toast";
import { useDispatch } from "react-redux";
import ChatSidebar from "../components/ChatSidebar";
import Header from "../components/Header";
import MessageList from "../components/MessageList";
import MessageInput from "../components/MessageInput";
import EmptyState from "../components/EmptyState";
import type { MediaPayload } from "../types";
import api from "../services/api";
import { logout as clearAuth } from "../redux/features/authSlice";
import type { AppDispatch } from "../redux/store";
import { useThreads } from "../hooks/useThreads";
import { useConversation } from "../hooks/useConversation";
import { useMediaProcessing } from "../hooks/useMediaProcessing";
import { createThreadId } from "../utils/createThreadId";

const MEDIA_LABELS: Record<string, string> = {
  youtube: "YouTube",
  audio: "Audio",
  video: "Video",
  document: "Document",
  text: "Text",
  dataset: "Dataset",
};

const Chat = () => {
  const [activeThreadId, _setActiveThreadId] = useState<string | null>(null);
  const activeThreadIdRef = useRef<string | null>(null); //
  const loadedThreadIdRef = useRef<string | null>(null);
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const dispatch = useDispatch<AppDispatch>();
  const navigate = useNavigate();

  const setActiveThreadId = useCallback((id: string) => {
    activeThreadIdRef.current = id;
    _setActiveThreadId(id);
  }, []);

  const { threads, isLoadingThreads, loadThreads, handleNewChat, setThreads } =
    useThreads();

  const {
    messages,
    activeStatus,
    isLoadingConversation,
    isSending,
    setMessages,
    setActiveStatus,
    loadConversation,
    abortStatusPolling,
    handleSend,
  } = useConversation();

  const { isProcessing, resetProcessing, handleProcessMedia } =
    useMediaProcessing();

  const activeTitle = useMemo(
    () =>
      threads.find((t) => t.thread_id === activeThreadId)?.title ?? "New Chat",
    [activeThreadId, threads],
  );

  const inputDisabled = isLoadingConversation;

  useEffect(() => {
    const id = window.setTimeout(() => void loadThreads(), 0);
    return () => window.clearTimeout(id);
  }, [loadThreads]);

  useEffect(() => {
    if (!activeThreadId) {
      loadedThreadIdRef.current = null;
      return;
    }

    if (activeThreadId === loadedThreadIdRef.current) return;

    const isPersistedThread = threads.some(
      (thread) => thread.thread_id === activeThreadId,
    );

    if (!isPersistedThread) {
      if (isLoadingThreads) return;
      loadedThreadIdRef.current = activeThreadId;
      return;
    }

    loadedThreadIdRef.current = activeThreadId;

    const id = window.setTimeout(
      () => void loadConversation(activeThreadId, false),
      0,
    );
    return () => window.clearTimeout(id);
  }, [activeThreadId, loadConversation, threads, isLoadingThreads]);

  const handleToggleSidebar = () => setIsSidebarOpen((prev) => !prev);

  const handleNewChatClick = () => {
    abortStatusPolling();
    resetProcessing();
    loadedThreadIdRef.current = null;
    handleNewChat(setActiveThreadId, setActiveStatus, setMessages);
  };

  const showCenteredEmptyLayout =
    messages.length === 0 && !activeStatus && !isProcessing;

  const getEnsuredThread = useCallback(() => {
    if (activeThreadIdRef.current) return activeThreadIdRef.current;

    const threadId = createThreadId();
    activeThreadIdRef.current = threadId;
    _setActiveThreadId(threadId);
    return threadId;
  }, []);

  const handleSendMessage = async (
    content: string,
    isApproval: boolean = false,
  ) => {
    await handleSend(
      content,
      activeThreadId,
      getEnsuredThread,
      setThreads,
      isApproval,
      false,
    );
  };

  const handleApproval = useCallback(
    (answer: "yes" | "no") => {
      setMessages((prev) =>
        prev.map((msg) =>
          "requires_approval" in msg && msg.requires_approval
            ? { ...msg, requires_approval: false, tool: undefined }
            : msg,
        ),
      );
      void handleSendMessage(answer, true);
    },
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [activeThreadId, getEnsuredThread, setThreads, handleSend, setMessages],
  );

  const handleProcessMediaClick = async (payload: MediaPayload) => {
    await handleProcessMedia(
      payload,
      getEnsuredThread,
      setActiveStatus,
      loadThreads,
    );

    const name =
      payload.file?.name ??
      payload.path ??
      MEDIA_LABELS[payload.media] ??
      payload.media;

    if (payload.media === "video" || payload.media === "audio") {
      setMessages((prev) => [
        ...prev,
        {
          id: `media-${Date.now()}`,
          role: "user" as const,
          content: `Uploaded ${payload.media}: ${name}`,
          mediaAttachment: { type: payload.media, name },
        },
      ]);
    }
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

  return (
    <div className="flex h-screen w-full overflow-hidden bg-slate-100 dark:bg-slate-950 text-slate-950 dark:text-white">
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

      <div className="flex min-w-0 flex-1 flex-col bg-white dark:bg-slate-950">
        <Header
          title={activeTitle}
          status={isProcessing ? (activeStatus ?? "processing") : activeStatus}
        />
        <div
          className={`flex flex-1 flex-col overflow-hidden${
            showCenteredEmptyLayout
              ? " items-center justify-center gap-8 px-4 "
              : ""
          }`}
        >
          {showCenteredEmptyLayout && <EmptyState />}
          {!showCenteredEmptyLayout && (
            <MessageList messages={messages} onApprove={handleApproval} />
          )}
          <div
            className={`w-full${showCenteredEmptyLayout ? " max-w-4xl" : " shrink-0"}`}
          >
            <MessageInput
              embedded={showCenteredEmptyLayout}
              disabled={inputDisabled}
              isSending={isSending}
              onSend={handleSendMessage}
              onProcessMedia={handleProcessMediaClick}
            />
          </div>
        </div>
      </div>
    </div>
  );
};

export default Chat;
