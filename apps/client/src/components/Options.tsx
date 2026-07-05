import { useRef } from "react";
import type { ChangeEvent } from "react";
import { AudioLines, FileText, SquarePlay, Video, File, TableProperties } from "lucide-react";
import OptionsButton from "./OptionsButton";
import type { MediaPayload } from "../types";

export type OptionsModal = "youtube" | "video" | "audio" | "text" | "document";

interface OptionsProps {
  isAnalystMode?: boolean;
  onDatasetUpload: (file: NonNullable<MediaPayload["file"]>) => Promise<void>;
  onOpenModal: (modal: OptionsModal) => void;
}

const Options = ({ isAnalystMode = false, onDatasetUpload, onOpenModal }: OptionsProps) => {
  const fileRef = useRef<HTMLInputElement>(null);

  const handleDatasetUpload = async (e: ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    await onDatasetUpload(file);
    if (fileRef.current) fileRef.current.value = "";
  };

  return (
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
            onClick={() => onOpenModal("youtube")}
          />

          <OptionsButton
            icon={<Video className="h-4 w-4" />}
            text="Video file"
            onClick={() => onOpenModal("video")}
          />

          <OptionsButton
            icon={<AudioLines className="h-4 w-4" />}
            text="Audio file"
            onClick={() => onOpenModal("audio")}
          />

          <OptionsButton
            icon={<FileText className="h-4 w-4" />}
            text="Text content"
            onClick={() => onOpenModal("text")}
          />

          <OptionsButton
            icon={<File className="h-4 w-4" />}
            text="Document (PDF)"
            onClick={() => onOpenModal("document")}
          />
        </>
      )}
    </div>
  );
};

export default Options;
