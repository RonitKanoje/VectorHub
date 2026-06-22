import { useCallback } from "react";
import toast from "react-hot-toast";
import { useDispatch } from "react-redux";
import api from "../services/api";
import { addDataset, addSystemMessage } from "../redux/features/analystSlice";
import type { AppDispatch } from "../redux/store";
import type { MediaPayload } from "../components/MessageInput";

/**
 * Encapsulates the dataset upload flow: POST /api/upload -> Redux dispatches + toast.
 */
export const useAnalystDatasetUpload = (threadId: string) => {
  const dispatch = useDispatch<AppDispatch>();

  const handleProcessMedia = useCallback(
    async (payload: MediaPayload) => {
      if (!payload.file) return;

      const fd = new FormData();
      fd.append("file", payload.file);
      fd.append("media", "dataset");
      fd.append("thread_id", threadId);

      try {
        const res = await api.post("/api/upload", fd, {
          headers: { "Content-Type": "multipart/form-data" },
        });

        if (res.data) {
          dispatch(
            addDataset({
              id: res.data.id ?? threadId,
              name: payload.file.name,
              thread_id: threadId,
              uploadedAt: new Date().toISOString(),
            }),
          );
          dispatch(
            addSystemMessage({
              content: `Dataset uploaded: **${payload.file.name}**. You can now ask questions about your data.`,
              mediaAttachment: { type: "dataset", name: payload.file.name },
            }),
          );
          toast.success(`${payload.file.name} uploaded successfully`);
        }
      } catch {
        toast.error("Upload failed");
      }
    },
    [dispatch, threadId],
  );

  return { handleProcessMedia };
};