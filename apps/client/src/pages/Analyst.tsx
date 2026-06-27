import { useState, useCallback, useRef, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import toast from "react-hot-toast";
import { useDispatch, useSelector } from "react-redux";
import ChatSidebar from "../components/ChatSidebar";
import Header from "../components/Header";
import MessageList from "../components/MessageList";
import AnalystDatasetPills from "../components/AnalystDatasetPills";
import MessageInput from "../components/MessageInput";
import EmptyState from "../components/EmptyState";
import api from "../services/api";
import { logout as clearAuth } from "../redux/features/authSlice";
// import { useAnalystAudioRecorder } from "../hooks/useAnalystAudioRecorder";
import { useAnalystDatasetUpload } from "../hooks/useAnalystDatasetUpload";
import { useAnalystChat } from "../hooks/useAnalystChat";
import { useThreads } from "../hooks/useThreads";
import { useAnalystConversation } from "../hooks/useAnalystConversation";
import type { RootState, AppDispatch } from "../redux/store";
import type { MediaPayload } from "../types";
import { createThreadId } from "../utils/createThreadId";
import { resetForNewChat } from "../redux/features/analystSlice";

const Analyst = () => {
  const [activeThreadId, _setActiveThreadId] = useState<string | null>(null);
  const activeThreadIdRef = useRef<string | null>(null);
  const loadedThreadIdRef = useRef<string | null>(null);
  // Tracks whether isSending was previously true so we can distinguish
  // "stream just ended" (isSending: true→false) from "thread switched".
  const wasStreamingRef = useRef(false);
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);

  const dispatch = useDispatch<AppDispatch>();
  const navigate = useNavigate();

  const messages = useSelector((s: RootState) => s.analyst.messages);
  const isSending = useSelector((s: RootState) => s.analyst.isSending);
  const uploadedDatasets = useSelector((s: RootState) => s.analyst.uploadedDatasets);
  const token = useSelector((s: RootState) => s.auth.accessToken);

  const setActiveThreadId = useCallback((id: string) => {
    activeThreadIdRef.current = id;
    _setActiveThreadId(id);
  }, []);

  const {
    threads,
    isLoadingThreads,
    loadThreads,
    handleNewChat,
    setThreads,
  } = useThreads();

  const { loadConversation } = useAnalystConversation();

  useEffect(() => {
    const id = window.setTimeout(() => void loadThreads("analyst"), 0);
    return () => window.clearTimeout(id);
  }, [loadThreads]);

  // Keep wasStreamingRef in sync with isSending so we can detect the
  // moment streaming finishes inside the conversation-reload effect.
  useEffect(() => {
    if (isSending) {
      wasStreamingRef.current = true;
    }
  }, [isSending]);

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

    // Skip reload immediately after streaming finishes — the streamed Redux
    // state (including visualizations) is the source of truth at this point.
    // The LangGraph checkpointer may not have persisted the state yet either.
    if (wasStreamingRef.current && !isSending) {
      wasStreamingRef.current = false; // reset for next message
      loadedThreadIdRef.current = activeThreadId;
      return;
    }

    loadedThreadIdRef.current = activeThreadId;

    const id = window.setTimeout(
      () => void loadConversation(activeThreadId),
      0,
    );
    return () => window.clearTimeout(id);
  }, [activeThreadId, loadConversation, isSending, threads, isLoadingThreads]);

  const handleToggleSidebar = () => setIsSidebarOpen((prev) => !prev);

  const handleNewChatClick = () => {
    dispatch(resetForNewChat());
    loadedThreadIdRef.current = null;
    handleNewChat(setActiveThreadId, () => {}, () => {});
  };

  const showCenteredEmptyLayout =
    messages.length === 0 && uploadedDatasets.length === 0;

  const handleAnalystProcessMedia = async (payload: MediaPayload) => {
    const name = payload.file?.name ?? payload.path ?? "Dataset";
    const content = `Uploaded dataset: ${name}`;

    await handleSend(
      content,
      getEnsuredThread(),
      setThreads
    );
    await handleProcessMedia(
      payload,
      getEnsuredThread,
      () => loadThreads("analyst"),
    );
  };

  const getEnsuredThread = useCallback(() => {
    if (activeThreadIdRef.current) return activeThreadIdRef.current;

    const threadId = createThreadId();
    activeThreadIdRef.current = threadId;
    _setActiveThreadId(threadId);
    return threadId;
  }, []);

  const { handleSend } = useAnalystChat(token);

  const { handleProcessMedia } = useAnalystDatasetUpload();

  const submitMessage = async (content: string) => {
    const threadId = getEnsuredThread();

    await handleSend(content, threadId, setThreads);
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
        <Header title="Analyst Mode" isAnalystMode={true} />

        <div
          className={`flex flex-1 flex-col overflow-hidden${
            showCenteredEmptyLayout
              ? " items-center justify-center gap-8 px-4"
              : ""
          }`}
        >
          {showCenteredEmptyLayout && <EmptyState isAnalystMode={true} />}
          {!showCenteredEmptyLayout && (
            <>
              <MessageList messages={messages} isAnalystMode={true} />
              <AnalystDatasetPills datasets={uploadedDatasets} />
            </>
          )}
          <div
            className={`w-full${showCenteredEmptyLayout ? " max-w-4xl" : " shrink-0"}`}
          >
            <MessageInput
              embedded={showCenteredEmptyLayout}
              isAnalystMode={true}
              onSend={submitMessage}
              isSending={isSending}
              onProcessMedia={handleAnalystProcessMedia}
            />
          </div>
        </div>
      </div>
    </div>
  );
};

export default Analyst;