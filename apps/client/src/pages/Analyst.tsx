import { useState, useCallback, useRef, useEffect, useMemo } from "react";
import { useNavigate } from "react-router-dom";
import toast from "react-hot-toast";
import { useDispatch, useSelector } from "react-redux";
import ChatSidebar from "../components/ChatSidebar";
import AnalystHeader from "../components/AnalystHeader";
import AnalystMessageList from "../components/AnalystMessageList";
import AnalystDatasetPills from "../components/AnalystDatasetPills";
import AnalystChatInput from "../components/AnalystChatInput";
import api from "../services/api";
import { logout as clearAuth } from "../redux/features/authSlice";
import { toggleTheme } from "../redux/features/themeSlice";
import { useAnalystAudioRecorder } from "../hooks/useAnalystAudioRecorder";
import { useAnalystDatasetUpload } from "../hooks/useAnalystDatasetUpload";
import { useAnalystChat } from "../hooks/useAnalystChat";
import { useThreads } from "../hooks/useThreads";
import { useAnalystConversation } from "../hooks/useAnalystConversation";
import type { RootState, AppDispatch } from "../redux/store";
import { createThreadId } from "../utils/createThreadId";
import { setMessages } from "../redux/features/analystSlice";

const Analyst = () => {
  const [activeThreadId, _setActiveThreadId] = useState<string | null>(null);
  const activeThreadIdRef = useRef<string | null>(null);
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [value, setValue] = useState("");

  const dispatch = useDispatch<AppDispatch>();
  const navigate = useNavigate();

  const messages = useSelector((s: RootState) => s.analyst.messages);
  const isSending = useSelector((s: RootState) => s.analyst.isSending);
  const uploadedDatasets = useSelector((s: RootState) => s.analyst.uploadedDatasets);
  const mode = useSelector((s: RootState) => s.theme.mode);
  const token = useSelector((s: RootState) => s.auth.accessToken);

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
    setThreads,
    setDraftThreadIds,
  } = useThreads();

  const { isLoadingConversation, loadConversation } = useAnalystConversation();

  useEffect(() => {
    const id = window.setTimeout(() => void loadThreads("analyst"), 0);
    return () => window.clearTimeout(id);
  }, [loadThreads]);

  useEffect(() => {
    if (!activeThreadId) return;

    if (isSending) return;

    const isDraft = draftThreadIds.has(activeThreadId);
    const id = window.setTimeout(
      () => void loadConversation(activeThreadId, isDraft),
      0,
    );
    return () => window.clearTimeout(id);
  }, [activeThreadId, draftThreadIds, loadConversation, isSending]);

  const handleToggleSidebar = () => setIsSidebarOpen((prev) => !prev);

  const handleNewChatClick = () =>
    handleNewChat(setActiveThreadId, () => { }, () => dispatch(setMessages([])));

  const getEnsuredThread = useCallback(() => {
    if (activeThreadIdRef.current) return activeThreadIdRef.current;

    const threadId = createThreadId();
    activeThreadIdRef.current = threadId;
    setDraftThreadIds((prev) => new Set(prev).add(threadId));
    setThreads((prev) => [{ thread_id: threadId, title: "New Analyst Chat" }, ...prev]);
    _setActiveThreadId(threadId);
    return threadId;
  }, [setThreads, setDraftThreadIds]);

  const { handleSend } = useAnalystChat(token);

  const { handleProcessMedia } = useAnalystDatasetUpload(getEnsuredThread);

  const { isRecording, isTranscribing, toggleRecording } = useAnalystAudioRecorder({
    onTranscript: (text) => setValue((p) => (p + " " + text).trim()),
  });

  const submitMessage = async (content: string) => {
    setValue("");
    const threadId = getEnsuredThread();

    await handleSend(content, threadId);
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
    <div className="flex h-screen w-full overflow-hidden bg-slate-950 text-white">
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

      <div className="flex min-w-0 flex-1 flex-col">
        <AnalystHeader mode={mode} onToggleTheme={() => dispatch(toggleTheme())} />

        <AnalystMessageList messages={messages} />

        <AnalystDatasetPills datasets={uploadedDatasets} />

        <AnalystChatInput
          value={value}
          onChange={setValue}
          onSend={() => submitMessage(value)}
          isSending={isSending}
          isRecording={isRecording}
          isTranscribing={isTranscribing}
          onToggleRecording={toggleRecording}
          onProcessMedia={handleProcessMedia}
        />
      </div>
    </div>
  );
};

export default Analyst;