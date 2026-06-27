import { useRef, useState } from "react";
import type { MediaPayload } from "../types";

interface VideoModalProps {
  isSubmitting: boolean;
  onClose: () => void;
  onSubmit: (file: NonNullable<MediaPayload["file"]>) => Promise<void>;
}

const VideoModal = ({ isSubmitting, onClose, onSubmit }: VideoModalProps) => {
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const [file, setFile] = useState<File | null>(null);

  const handleSubmit = async () => {
    if (!file || isSubmitting) return;
    await onSubmit(file);
  };

  return (
    <div className="flex max-h-[calc(100vh-4rem)] w-full flex-col gap-6 overflow-y-auto rounded-2xl bg-white p-5 shadow-2xl sm:p-8">
      <div>
        <h1 className="text-2xl font-bold text-slate-950">Upload Video</h1>

        <p className="mt-1 text-sm text-slate-500">
          Upload a video file to extract audio and process chunks.
        </p>
      </div>

      <input
        ref={fileInputRef}
        type="file"
        accept="video/*"
        className="hidden"
        onChange={(e) => setFile(e.target.files?.[0] || null)}
      />

      <button
        type="button"
        disabled={isSubmitting}
        className="flex min-h-24 w-full items-center justify-center break-all rounded-xl border-2 border-dashed border-slate-300 px-4 text-center text-sm text-slate-600 transition hover:border-cyan-500 hover:text-cyan-700 disabled:cursor-not-allowed disabled:opacity-60"
        onClick={() => fileInputRef.current?.click()}
      >
        {file ? file.name : "Choose a video file"}
      </button>

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
          disabled={!file || isSubmitting}
          className="rounded-xl bg-slate-950 px-5 py-2 text-sm font-semibold text-white transition hover:bg-cyan-700 active:scale-95 disabled:cursor-not-allowed disabled:bg-slate-300"
          onClick={() => void handleSubmit()}
        >
          {isSubmitting ? "Processing..." : "Submit"}
        </button>
      </div>
    </div>
  );
};

export default VideoModal;
