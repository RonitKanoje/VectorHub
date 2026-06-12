import toast from "react-hot-toast";
import api from "../services/api";

function wait(ms: number) {
  return new Promise((resolve) => {
    window.setTimeout(resolve, ms);
  });
}

export async function pollThreadStatus(
  threadId: string,
  onStatus: (status: string) => void,
  options: { maxDurationMs?: number; signal?: AbortSignal } = {},
) {
  const maxDuration = options.maxDurationMs ?? 15 * 60 * 1000;
  const startTime = Date.now();

  const getInterval = (attempt: number) => {
    if (attempt < 10) return 1500; // first 15s: every 1.5s
    if (attempt < 30) return 5_000; // next 2.5min: every 5s
    return 30_000; // after that: every 30s
  };

  for (let attempt = 0; ; attempt += 1) {
    await wait(getInterval(attempt));

    // Stop if the caller cancelled (e.g. user switched threads)
    if (options.signal?.aborted) return;

    if (Date.now() - startTime >= maxDuration) {
      onStatus("pending");
      toast("Still processing — come back later to continue chatting.");
      return;
    }

    const response = await api.get<{ status: string }>(
      `/api/ai/ingestion_status/${threadId}`,
    );
    const status = response.data.status;
    onStatus(status);

    if (status === "completed") {
      toast.success("Content is ready for chat");
      return;
    }
    if (status.startsWith("failed")) {
      throw new Error(status);
    }
  }
}
