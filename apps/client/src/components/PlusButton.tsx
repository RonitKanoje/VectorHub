import { useState } from "react";
import { Plus } from "lucide-react";
import Options from "./Options";
import type { MediaPayload } from "./MessageInput";

interface PlusButtonProps {
  disabled?: boolean;
  onProcessMedia: (payload: MediaPayload) => Promise<void>;
}

const PlusButton = ({ disabled = false, onProcessMedia }: PlusButtonProps) => {
  const [showOptions, setShowOptions] = useState(false);

  return (
    <div className="absolute left-3 top-1/2 z-20 -translate-y-1/2">
      <button
        type="button"
        disabled={disabled}
        className="flex h-9 w-9 items-center justify-center rounded-xl text-slate-600 transition hover:bg-slate-200 hover:text-slate-950 disabled:cursor-not-allowed disabled:text-slate-300"
        onClick={() => setShowOptions((prev) => !prev)}
        aria-label="Add content"
      >
        <Plus className="h-5 w-5" />
      </button>

      {showOptions && (
        <div className="fixed bottom-24 left-3 z-50 w-[calc(100vw-1.5rem)] max-w-64 rounded-2xl border border-slate-200 bg-white p-2 shadow-2xl shadow-slate-950/15 sm:absolute sm:bottom-full sm:left-0 sm:mb-3 sm:w-64">
          <Options
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
