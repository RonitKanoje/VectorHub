import { useState } from "react";

interface YTModalProps {
  isSubmitting: boolean;
  onClose: () => void;
  onSubmit: (path: string) => Promise<void>;
}

const YTModal = ({ isSubmitting, onClose, onSubmit }: YTModalProps) => {
  const [url, setUrl] = useState("");

  return (
    <div className="flex max-h-[calc(100vh-4rem)] w-full flex-col gap-6 overflow-y-auto rounded-2xl bg-white p-5 shadow-2xl sm:p-8">
      <div>
        <h1 className="text-2xl font-bold text-slate-950">YouTube Transcript</h1>

        <p className="mt-1 text-sm text-slate-500">
          Paste a YouTube URL and it will be chunked for this chat.
        </p>
      </div>

      <input
        type="text"
        value={url}
        disabled={isSubmitting}
        placeholder="https://youtube.com/watch?v=..."
        className="h-12 w-full rounded-xl border border-slate-300 px-4 text-sm outline-none transition focus:border-cyan-500 focus:ring-2 focus:ring-cyan-500/20 disabled:bg-slate-100"
        onChange={(e) => setUrl(e.target.value)}
      />

      <div className="flex justify-end gap-3">
        <button
          type="button"
          disabled={isSubmitting}
          className="rounded-xl border border-slate-300 px-4 py-2 text-sm text-slate-700 transition hover:bg-slate-100 disabled:cursor-not-allowed disabled:opacity-60"
          onClick={onClose}
        >
          Cancel
        </button>

        <button
          type="button"
          disabled={!url.trim() || isSubmitting}
          className="rounded-xl bg-slate-950 px-5 py-2 text-sm font-semibold text-white transition hover:bg-cyan-700 active:scale-95 disabled:cursor-not-allowed disabled:bg-slate-300"
          onClick={() => onSubmit(url.trim())}
        >
          {isSubmitting ? "Processing..." : "Submit"}
        </button>
      </div>
    </div>
  );
};

export default YTModal;
