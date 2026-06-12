import { useState } from "react";

interface TextModalProps {
  isSubmitting: boolean;
  onClose: () => void;
  onSubmit: (path: string) => Promise<void>;
}

const TextModal = ({ isSubmitting, onClose, onSubmit }: TextModalProps) => {
  const [text, setText] = useState("");

  return (
    <div className="flex max-h-[calc(100vh-4rem)] w-full flex-col gap-6 overflow-y-auto rounded-2xl bg-white p-5 shadow-2xl sm:p-8">
      <div>
        <h1 className="text-2xl font-bold text-slate-950">Text Content</h1>

        <p className="mt-1 text-sm text-slate-500">
          Paste text to process it into searchable chunks.
        </p>
      </div>

      <textarea
        value={text}
        disabled={isSubmitting}
        placeholder="Paste your text here..."
        className="h-48 max-h-[40vh] w-full resize-none rounded-xl border border-slate-300 p-4 text-sm outline-none transition focus:border-cyan-500 focus:ring-2 focus:ring-cyan-500/20 disabled:bg-slate-100"
        onChange={(e) => setText(e.target.value)}
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
          disabled={!text.trim() || isSubmitting}
          className="rounded-xl bg-slate-950 px-5 py-2 text-sm font-semibold text-white transition hover:bg-cyan-700 active:scale-95 disabled:cursor-not-allowed disabled:bg-slate-300"
          onClick={() => onSubmit(text.trim())}
        >
          {isSubmitting ? "Processing..." : "Submit"}
        </button>
      </div>
    </div>
  );
};

export default TextModal;
