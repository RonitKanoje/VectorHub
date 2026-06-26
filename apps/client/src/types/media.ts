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

/** A single uploaded item shown as a pill in the chat input area. */
// export interface UploadedItem {
//   type: string;
//   name: string;
//   icon?: string;
// }
