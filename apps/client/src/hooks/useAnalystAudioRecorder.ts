import { useRef, useState } from "react";
import toast from "react-hot-toast";
import api from "../services/api";

interface UseAnalystAudioRecorderOptions {
  onTranscript: (text: string) => void;
}

/**
 * Encapsulates mic capture -> /api/ai/transcribe -> onTranscript callback.
 * Keeps Analyst.tsx free of MediaRecorder plumbing.
 */
export const useAnalystAudioRecorder = ({ onTranscript }: UseAnalystAudioRecorderOptions) => {
  const [isRecording, setIsRecording] = useState(false);
  const [isTranscribing, setIsTranscribing] = useState(false);

  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      audioChunksRef.current = [];
      const mr = new MediaRecorder(stream, { mimeType: "audio/webm" });
      mediaRecorderRef.current = mr;

      mr.ondataavailable = (e) => {
        if (e.data.size > 0) audioChunksRef.current.push(e.data);
      };

      mr.onstop = async () => {
        setIsTranscribing(true);
        try {
          const blob = new Blob(audioChunksRef.current, { type: "audio/webm" });
          const fd = new FormData();
          fd.append("audio", blob, "recording.webm");
          const res = await api.post<{ text: string }>("/api/ai/transcribe", fd, {
            headers: { "Content-Type": "multipart/form-data" },
          });
          if (res.data.text) onTranscript(res.data.text);
        } catch {
          toast.error("Transcription failed");
        } finally {
          setIsTranscribing(false);
          stream.getTracks().forEach((t) => t.stop());
        }
      };

      mr.start();
      setIsRecording(true);
    } catch {
      toast.error("Microphone access denied");
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current?.state !== "inactive") {
      mediaRecorderRef.current?.stop();
    }
    setIsRecording(false);
  };

  const toggleRecording = () => (isRecording ? stopRecording() : startRecording());

  return { isRecording, isTranscribing, startRecording, stopRecording, toggleRecording };
};