// ─── Analyst domain types ─────────────────────────────────────────────────────

import type { MediaAttachment } from "./chat";

/** A chart artifact streamed or reloaded from the backend. */
export interface AnalystVisualization {
  type: "visualization";
  /** Base-64 encoded PNG. */
  image: string;
  chart_type: string;
  title: string;
  summary?: string;
}

/**
 * A single message in the Analyst conversation.
 * Used by both the Redux slice and the UI components.
 */
export interface AnalystMessage {
  id: string;
  role: "user" | "assistant" | "system";
  content: string;
  pending?: boolean;
  mediaAttachment?: MediaAttachment;
  visualizations?: AnalystVisualization[];
}

/** A dataset that has been uploaded and processed for a given thread. */
export interface AnalystDataset {
  id: string;
  name: string;
  thread_id: string;
  uploadedAt: string;
}