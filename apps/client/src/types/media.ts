/** Discriminated union of all supported media ingest types. */
export type MediaType =
  | "youtube"
  | "audio"
  | "video"
  | "text"
  | "document"
  | "dataset";

/** Payload sent to /api/upload when the user submits a media item. */
export interface MediaPayload {
  media: MediaType;
  path?: string;
  language?: string | null;
  file?: File;
}

export interface UseMediaProcessingReturn {
  isProcessing: boolean;
  resetProcessing: () => void;
  handleProcessMedia: (
    payload: MediaPayload,
    ensureActiveThread: () => string,
    setActiveStatus: (status: string | null) => void,
    loadThreads: () => Promise<void>,
  ) => Promise<void>;
}

