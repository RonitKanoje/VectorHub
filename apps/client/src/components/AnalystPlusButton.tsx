import { useState, useRef } from "react";
import { Plus, TableProperties } from "lucide-react";
import type { MediaPayload } from "../types";

interface AnalystPlusButtonProps {
  disabled?: boolean;
  onProcessMedia: (payload: MediaPayload) => Promise<void>;
}

const AnalystPlusButton = ({ disabled = false, onProcessMedia }: AnalystPlusButtonProps) => {
  const [showOptions, setShowOptions] = useState(false);
  const fileRef = useRef<HTMLInputElement>(null);

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setShowOptions(false);
    await onProcessMedia({ media: "dataset", file });
    e.target.value = "";
  };

  return (
    <div className="absolute left-3 top-1/2 z-20 -translate-y-1/2">
      <button
        type="button"
        disabled={disabled}
        className="flex h-9 w-9 items-center justify-center rounded-xl text-violet-600 dark:text-violet-400 transition hover:bg-violet-100 dark:hover:bg-violet-900/40 disabled:cursor-not-allowed disabled:opacity-40"
        onClick={() => setShowOptions((prev) => !prev)}
        aria-label="Upload dataset"
      >
        <Plus className="h-5 w-5" />
      </button>

      {showOptions && (
        <div className="fixed bottom-24 left-3 z-50 w-64 rounded-2xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 p-2 shadow-2xl sm:absolute sm:bottom-full sm:left-0 sm:mb-3">
          <p className="px-3 py-1.5 text-xs font-semibold uppercase tracking-wider text-slate-400">
            Upload Dataset
          </p>

          {/* CSV / Excel */}
          <button
            type="button"
            className="flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-left text-sm text-slate-700 dark:text-slate-200 transition hover:bg-violet-50 dark:hover:bg-violet-900/30"
            onClick={() => fileRef.current?.click()}
          >
            <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-violet-100 dark:bg-violet-900/40 text-violet-600 dark:text-violet-400">
              <TableProperties className="h-4 w-4" />
            </span>
            <div>
              <p className="font-medium">CSV / Excel</p>
              <p className="text-xs text-slate-400">.csv, .xlsx, .xls</p>
            </div>
          </button>

          <input
            ref={fileRef}
            type="file"
            accept=".csv,.xlsx,.xls"
            className="hidden"
            onChange={handleFileChange}
          />
        </div>
      )}

      {/* Click outside to close */}
      {showOptions && (
        <div className="fixed inset-0 z-40" onClick={() => setShowOptions(false)} />
      )}
    </div>
  );
};

export default AnalystPlusButton;
