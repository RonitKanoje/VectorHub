import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import toast from "react-hot-toast";
import { useDispatch } from "react-redux";
import ChatSidebar from "../components/ChatSidebar";
import ChatHeader from "../components/ChatHeader";
import ChatMessagePanel from "../components/ChatMessagePanel";
import type { MediaPayload, UploadedItem } from "../components/MessageInput";
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
  const activeThreadIdRef = useRef<string | null>(null);
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [uploadedItems, setUploadedItems] = useState<UploadedItem[]>([]);
  const dispatch = useDispatch<AppDispatch>();
  const navigate = useNavigate();

  const setActiveThreadId = useCallback((id: string) => {
    activeThreadIdRef.current = id;
    _setActiveThreadId(id);
  }, []);

  const {
    threads,
    isLoadingThreads,
    draftThreadIds,
    loadThreads,
    handleNewChat,
    removeDraftThread,
    setThreads,
    setDraftThreadIds,
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
    if (!activeThreadId) return;

    // ✅ KEY FIX: Don't wipe messages while a send is in progress
    if (isSending) return;

    const isDraft = draftThreadIds.has(activeThreadId);
    const id = window.setTimeout(
      () => void loadConversation(activeThreadId, isDraft),
      0,
    );
    return () => window.clearTimeout(id);
  }, [activeThreadId, draftThreadIds, loadConversation, isSending]);

  useEffect(() => {
    setUploadedItems([]);
  }, [activeThreadId]);

  const handleToggleSidebar = () => setIsSidebarOpen((prev) => !prev);

  const handleNewChatClick = () =>
    handleNewChat(setActiveThreadId, setActiveStatus, setMessages);

  const getEnsuredThread = useCallback(() => {
    if (activeThreadIdRef.current) return activeThreadIdRef.current;

    const threadId = createThreadId();
    activeThreadIdRef.current = threadId;
    setDraftThreadIds((prev) => new Set(prev).add(threadId));
    setThreads((prev) => [{ thread_id: threadId, title: "New Chat" }, ...prev]);
    _setActiveThreadId(threadId);
    return threadId;
  }, [setThreads, setDraftThreadIds]);

  const handleSendMessage = async (
    content: string,
    isApproval: boolean = false,
  ) => {
    await handleSend(
      content,
      activeThreadId,
      getEnsuredThread,
      removeDraftThread,
      setThreads,
      isApproval,
      false,
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

    const name =
      payload.file?.name ??
      payload.path ??
      MEDIA_LABELS[payload.media] ??
      payload.media;

    setUploadedItems((prev) => [
      ...prev,
      { type: payload.media, name, icon: "" },
    ]);

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

  const handleRemoveUpload = (index: number) => {
    setUploadedItems((prev) => prev.filter((_, i) => i !== index));
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
        <ChatHeader
          title={activeTitle}
          status={isProcessing ? (activeStatus ?? "processing") : activeStatus}
        />
        <ChatMessagePanel
          messages={messages}
          disabled={inputDisabled}
          isSending={isSending}
          uploadedItems={uploadedItems}
          onSend={handleSendMessage}
          onProcessMedia={handleProcessMediaClick}
          onRemoveUpload={handleRemoveUpload}
        />
      </div>
    </div>
  );
};

export default Chat;
