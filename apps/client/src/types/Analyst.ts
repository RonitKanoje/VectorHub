export interface AnalystMediaAttachment {
  type: string;
  name: string;
}

export interface AnalystChatMessage {
  id: string;
  role: "user" | "assistant" | "system";
  content: string;
  pending?: boolean;
  mediaAttachment?: AnalystMediaAttachment;
}

export interface AnalystUploadedDataset {
  id: string;
  name: string;
  thread_id: string;
  uploadedAt: string;
}