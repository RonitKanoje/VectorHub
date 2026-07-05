import { useEffect, useRef, useState } from "react";
import { createPortal } from "react-dom";
import { Plus } from "lucide-react";
import Options from "./Options";
import type { OptionsModal } from "./Options";
import YTModal from "./YTModal";
import VideoModal from "./VideoModal";
import AudioModal from "./AudioModal";
import TextModal from "./TextModal";
import DocumentModal from "./DocumentModal";
import type { MediaPayload } from "../types";

type ActiveModal = OptionsModal | null;
const modalBackdropClass =
  "fixed inset-0 z-[100] flex items-center justify-center overflow-y-auto bg-slate-950/60 px-4 py-6 backdrop-blur-sm";
const modalShellClass = "w-full max-w-lg";

interface PlusButtonProps {
  disabled?: boolean;
  isAnalystMode?: boolean;
  onProcessMedia: (payload: MediaPayload) => Promise<void>;
}

const PlusButton = ({
  disabled = false,
  isAnalystMode = false,
  onProcessMedia,
}: PlusButtonProps) => {
  const [showOptions, setShowOptions] = useState(false);
  const [activeModal, setActiveModal] = useState<ActiveModal>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!showOptions || activeModal) return;

    const handleOutsideClick = (event: MouseEvent | TouchEvent) => {
      const target = event.target as Node | null;

      if (target && containerRef.current?.contains(target)) {
        return;
      }

      setShowOptions(false);
    };

    document.addEventListener("mousedown", handleOutsideClick);
    document.addEventListener("touchstart", handleOutsideClick);

    return () => {
      document.removeEventListener("mousedown", handleOutsideClick);
      document.removeEventListener("touchstart", handleOutsideClick);
    };
  }, [activeModal, showOptions]);

  const handleOpenModal = (modal: OptionsModal) => {
    setActiveModal(modal);
    setShowOptions(false);
  };

  const handleSubmit = async (payload: MediaPayload) => {
    setIsSubmitting(true);
    try {
      await onProcessMedia(payload);
      setActiveModal(null);
      setShowOptions(false);
    } finally {
      setIsSubmitting(false);
    }
  };

  const closeModal = () => {
    if (!isSubmitting) {
      setActiveModal(null);
    }
  };

  const modal =
    activeModal && typeof document !== "undefined"
      ? createPortal(
          <div className={modalBackdropClass} onClick={closeModal}>
            <div className={modalShellClass} onClick={(e) => e.stopPropagation()}>
              {activeModal === "youtube" && (
                <YTModal
                  isSubmitting={isSubmitting}
                  onClose={closeModal}
                  onSubmit={(path) => handleSubmit({ media: "youtube", path })}
                />
              )}

              {activeModal === "video" && (
                <VideoModal
                  isSubmitting={isSubmitting}
                  onClose={closeModal}
                  onSubmit={(file) => handleSubmit({ media: "video", file })}
                />
              )}

              {activeModal === "audio" && (
                <AudioModal
                  isSubmitting={isSubmitting}
                  onClose={closeModal}
                  onSubmit={(file) => handleSubmit({ media: "audio", file })}
                />
              )}

              {activeModal === "text" && (
                <TextModal
                  isSubmitting={isSubmitting}
                  onClose={closeModal}
                  onSubmit={(path) => handleSubmit({ media: "text", path })}
                />
              )}

              {activeModal === "document" && (
                <DocumentModal
                  isSubmitting={isSubmitting}
                  onClose={closeModal}
                  onSubmit={(file) => handleSubmit({ media: "document", file })}
                />
              )}
            </div>
          </div>,
          document.body,
        )
      : null;

  return (
    <div ref={containerRef} className="absolute left-3 top-1/2 z-20 -translate-y-1/2">
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
            onDatasetUpload={(file) => handleSubmit({ media: "dataset", file })}
            onOpenModal={handleOpenModal}
          />
        </div>
      )}

      {modal}
    </div>
  );
};

export default PlusButton;
