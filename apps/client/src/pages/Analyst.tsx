import { useState } from "react";
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
import type { RootState, AppDispatch } from "../redux/store";
import { createThreadId } from "../utils/createThreadId";

const Analyst = () => {
  const dispatch = useDispatch<AppDispatch>();
  const navigate = useNavigate();

  const messages = useSelector((s: RootState) => s.analyst.messages);
  const isSending = useSelector((s: RootState) => s.analyst.isSending);
  const uploadedDatasets = useSelector((s: RootState) => s.analyst.uploadedDatasets);
  const mode = useSelector((s: RootState) => s.theme.mode);
  const token = useSelector((s: RootState) => s.auth.accessToken);

  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [value, setValue] = useState("");
  const [threadId] = useState(() => createThreadId()); // by doing this we are preventing the change of value at the time of re-rendering we avoided useEffect because here we are not doing any kind of heavy calc so avoid that 

  const { handleSend } = useAnalystChat(threadId, token);
  const { handleProcessMedia } = useAnalystDatasetUpload(threadId);
  const { isRecording, isTranscribing, toggleRecording } = useAnalystAudioRecorder({
    onTranscript: (text) => setValue((p) => (p + " " + text).trim()),
  });

  const submitMessage = (content: string) => {
    setValue("");
    void handleSend(content);
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
        onToggleSidebar={() => setIsSidebarOpen((p) => !p)}
        threads={uploadedDatasets.map((d) => ({
          thread_id: d.id,
          title: d.name,
        }))}
        activeThreadId={uploadedDatasets[0]?.id ?? null}
        isLoadingThreads={false}
        onNewChat={() => navigate("/analyst")}
        onSelectThread={() => {}}
        onLogout={() => void handleLogout()}
        onLogoutAll={() => void handleLogoutAll()}
      />

      <div className="flex min-w-0 flex-1 flex-col">
        <AnalystHeader mode={mode} onToggleTheme={() => dispatch(toggleTheme())} />

        <AnalystMessageList messages={messages} onSelectPrompt={submitMessage} />

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