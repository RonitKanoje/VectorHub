// ─── Chat domain types ────────────────────────────────────────────────────────

export type ChatRole = "user" | "assistant";

/** Shared media attachment pill shown on messages in both Chat and Analyst. */
export interface MediaAttachment {
  type: string;
  name: string;
}

/** A single message in the main (RAG) chat conversation. */
export interface ChatMessage {
  id: string;
  role: ChatRole;
  content: string;
  pending?: boolean;
  requires_approval?: boolean;
  tool?: string;
  mediaAttachment?: MediaAttachment;
}
