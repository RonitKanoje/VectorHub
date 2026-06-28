import { useState } from "react";
import { Plus } from "lucide-react";
import Options from "./Options";
import type { MediaPayload } from "../types";

interface PlusButtonProps {
  disabled?: boolean;
  isAnalystMode?: boolean;
  onProcessMedia: (payload: MediaPayload) => Promise<void>;
}

const PlusButton = ({ disabled = false, isAnalystMode = false, onProcessMedia }: PlusButtonProps) => {
  const [showOptions, setShowOptions] = useState(false);

  return (
    <div className="absolute left-3 top-1/2 z-20 -translate-y-1/2">
      <button
        type="button"
        disabled={disabled}
        className="flex h-9 w-9 items-center justify-center rounded-xl text-slate-600 dark:text-slate-400 transition hover:bg-slate-200 dark:hover:bg-slate-800 hover:text-slate-950 dark:hover:text-white disabled:cursor-not-allowed disabled:text-slate-300 dark:disabled:text-slate-600"
        onClick={() => setShowOptions((prev) => !prev)}
        aria-label="Add content"
      >
        <Plus className="h-5 w-5" />
      </button>

      {showOptions && (
        <div className="fixed bottom-24 left-3 z-50 w-[calc(100vw-1.5rem)] max-w-64 rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-2 shadow-2xl shadow-slate-950/15 sm:absolute sm:bottom-full sm:left-0 sm:mb-3 sm:w-64">
          <Options
            isAnalystMode={isAnalystMode}
            onClose={() => setShowOptions(false)}
            onProcessMedia={async (payload) => {
              await onProcessMedia(payload);
              setShowOptions(false);
            }}
          />
        </div>
      )}
    </div>
  );
};

export default PlusButton;
