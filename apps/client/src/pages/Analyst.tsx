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
  const wasStreamingRef = useRef(false);
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);

  const dispatch = useDispatch<AppDispatch>();
  const navigate = useNavigate();

  const messages = useSelector((s: RootState) => s.analyst.messages);
  const isSending = useSelector((s: RootState) => s.analyst.isSending);
  const uploadedDatasets = useSelector(
    (s: RootState) => s.analyst.uploadedDatasets,
  );
  const token = useSelector((s: RootState) => s.auth.accessToken);

  const setActiveThreadId = useCallback((id: string) => {
    console.log("setActiveThreadId called", {
      previousActiveThreadId: activeThreadIdRef.current,
      newId: id,
    });
    console.trace();
    console.log("Setting active thread:", id);
    activeThreadIdRef.current = id;
    _setActiveThreadId(id);
  }, []);

  const { threads, isLoadingThreads, loadThreads, handleNewChat, setThreads } =
    useThreads();

  useEffect(() => {
    console.log("✅ Analyst mounted");

    return () => {
      console.log("❌ Analyst unmounted");
    };
  }, []);

  useEffect(() => {
    console.log({
      activeThreadId,
      messages: messages.length,
      uploadedDatasets: uploadedDatasets.length,
    });
  }, [activeThreadId, messages, uploadedDatasets]);

  const { loadConversation } = useAnalystConversation();

  useEffect(() => {
    const id = window.setTimeout(() => {
      console.log("Loading analyst thread list");
      void loadThreads("analyst").then(() => {
        console.log("Finished loading analyst thread list");
      });
    }, 0);
    return () => window.clearTimeout(id);
  }, [loadThreads]);

  useEffect(() => {
    dispatch(resetForNewChat());
  }, []);

  useEffect(() => {
    if (isSending) {
      wasStreamingRef.current = true;
    }
  }, [isSending]);

  useEffect(() => {
    console.log("Thread loading effect started", {
      activeThreadId,
      loadedThreadIdRefCurrent: loadedThreadIdRef.current,
      isSending,
      isLoadingThreads,
      threadCount: threads.length,
    });

    if (!activeThreadId) {
      console.log("Branch: no active thread");
      loadedThreadIdRef.current = null;
      return;
    }

    if (activeThreadId === loadedThreadIdRef.current) {
      console.log("Branch: already loaded");
      return;
    }

    const isPersistedThread = threads.some(
      (thread) => thread.thread_id === activeThreadId,
    );

    if (!isPersistedThread) {
      if (isLoadingThreads) {
        console.log("Branch: waiting for threads");
        return;
      }
      console.log("Branch: new temporary thread");
      loadedThreadIdRef.current = activeThreadId;
      return;
    }

    console.log("Branch: persisted thread found");

    if (wasStreamingRef.current && !isSending) {
      console.log("Branch: skipping because stream just finished");
      wasStreamingRef.current = false; // reset for next message
      loadedThreadIdRef.current = activeThreadId;
      return;
    }

    loadedThreadIdRef.current = activeThreadId;

    console.log("Branch: about to call loadConversation()");
    const id = window.setTimeout(() => {
      console.log("Loading conversation:", activeThreadId);
      void loadConversation(activeThreadId);
    }, 0);
    console.log("Conversation scheduled");
    return () => window.clearTimeout(id);
  }, [activeThreadId, loadConversation, isSending, threads, isLoadingThreads]);

  const handleToggleSidebar = () => setIsSidebarOpen((prev) => !prev);

  const handleNewChatClick = () => {
    console.log("New Chat clicked");
    console.log("activeThreadId before reset:", activeThreadId);
    dispatch(resetForNewChat());
    loadedThreadIdRef.current = null;
    console.log("activeThreadId after reset:", activeThreadId);
    handleNewChat(
      setActiveThreadId,
      () => {},
      () => {},
    );
  };

  const showCenteredEmptyLayout =
    messages.length === 0 && uploadedDatasets.length === 0;

  const handleAnalystProcessMedia = async (payload: MediaPayload) => {
    console.log("handleAnalystProcessMedia payload:", payload);
    // const name = payload.file?.name ?? payload.path ?? "Dataset";
    // const content = `Uploaded dataset: ${name}`;

    // await handleSend(
    //   content,
    //   getEnsuredThread(),
    //   setThreads
    // );
    await handleProcessMedia(
      payload,
      () => {
        const threadId = getEnsuredThread();
        console.log("handleAnalystProcessMedia ensured thread:", threadId);
        return threadId;
      },
      () => loadThreads("analyst"),
    );
  };

  const getEnsuredThread = useCallback(() => {
    if (activeThreadIdRef.current) {
      console.log(
        "getEnsuredThread: reused existing thread",
        activeThreadIdRef.current,
      );
      return activeThreadIdRef.current;
    }

    const threadId = createThreadId();
    activeThreadIdRef.current = threadId;
    _setActiveThreadId(threadId);
    console.log("getEnsuredThread: created new thread", threadId);
    return threadId;
  }, []);

  const { handleSend } = useAnalystChat(token);

  const { handleProcessMedia } = useAnalystDatasetUpload();

  const submitMessage = async (content: string) => {
    const threadId = getEnsuredThread();
    console.log("submitMessage", { content, threadId });

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
