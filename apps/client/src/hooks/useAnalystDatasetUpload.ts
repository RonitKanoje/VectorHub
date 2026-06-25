import { useCallback } from "react";
import toast from "react-hot-toast";
import { useDispatch } from "react-redux";
import api from "../services/api";
import { addDataset } from "../redux/features/analystSlice";
import type { AppDispatch } from "../redux/store";
import type { MediaPayload } from "../components/MessageInput";

/**
 * Encapsulates the dataset upload flow: POST /api/upload -> Redux dispatches + toast.
 */
export const useAnalystDatasetUpload = (getEnsuredThread: () => string) => {
  const dispatch = useDispatch<AppDispatch>();

  const handleProcessMedia = useCallback(
    async (payload: MediaPayload) => {
      if (!payload.file) return;

      const threadId = getEnsuredThread();

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
          toast.success(`${payload.file.name} uploaded successfully`);
        }
      } catch {
        toast.error("Upload failed");
      }
    },
    [dispatch, getEnsuredThread],
  );

  return { handleProcessMedia };
};
