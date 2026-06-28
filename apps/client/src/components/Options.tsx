import { useRef, useState } from "react";
import { createPortal } from "react-dom";
import { AudioLines, FileText, SquarePlay, Video, File, TableProperties } from "lucide-react";
import OptionsButton from "./OptionsButton";
import YTModal from "./YTModal";
import VideoModal from "./VideoModal";
import AudioModal from "./AudioModal";
import TextModal from "./TextModal";
import DocumentModal from "./DocumentModal";
import type { MediaPayload } from "../types";

type ActiveModal = "youtube" | "video" | "audio" | "text" | "document" | null;
const modalBackdropClass =
  "fixed inset-0 z-[100] flex items-center justify-center overflow-y-auto bg-slate-950/60 px-4 py-6 backdrop-blur-sm";
const modalShellClass = "w-full max-w-lg";

interface OptionsProps {
  isAnalystMode?: boolean;
  onClose: () => void;
  onProcessMedia: (payload: MediaPayload) => Promise<void>;
}

const Options = ({ isAnalystMode = false, onClose, onProcessMedia }: OptionsProps) => {
  const [activeModal, setActiveModal] = useState<ActiveModal>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const fileRef = useRef<HTMLInputElement>(null);

  const handleDatasetUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    await handleSubmit({ media: "dataset", file });
    if (fileRef.current) fileRef.current.value = "";
  };

  const handleSubmit = async (payload: MediaPayload) => {
    setIsSubmitting(true);
    try {
      await onProcessMedia(payload);
      setActiveModal(null);
      onClose();
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
    <>
      <div className="flex flex-col gap-1">
        {isAnalystMode ? (
          <>
            <p className="px-3 py-1.5 text-xs font-semibold uppercase tracking-wider text-slate-400 dark:text-slate-500">
              Upload Dataset
            </p>
            <OptionsButton
              icon={<TableProperties className="h-4 w-4" />}
              text="CSV / Excel"
              subtitle=".csv, .xlsx, .xls"
              onClick={() => fileRef.current?.click()}
            />
            <input
              ref={fileRef}
              type="file"
              accept=".csv,.xlsx,.xls"
              className="hidden"
              onChange={handleDatasetUpload}
            />
          </>
        ) : (
          <>
            <OptionsButton
              icon={<SquarePlay className="h-4 w-4" />}
              text="YouTube transcript"
              onClick={() => setActiveModal("youtube")}
            />

            <OptionsButton
              icon={<Video className="h-4 w-4" />}
              text="Video file"
              onClick={() => setActiveModal("video")}
            />

            <OptionsButton
              icon={<AudioLines className="h-4 w-4" />}
              text="Audio file"
              onClick={() => setActiveModal("audio")}
            />

            <OptionsButton
              icon={<FileText className="h-4 w-4" />}
              text="Text content"
              onClick={() => setActiveModal("text")}
            />

            <OptionsButton
              icon={<File className="h-4 w-4" />}
              text="Document (PDF)"
              onClick={() => setActiveModal("document")}
            />
          </>
        )}
      </div>

      {modal}
    </>
  );
};

export default Options;
