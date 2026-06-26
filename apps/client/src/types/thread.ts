// ─── Thread domain types ──────────────────────────────────────────────────────

/** Chat mode selector for thread filtering. */
export type ThreadMode = "chat" | "analyst";

/** A chat thread entry shown in the sidebar. */
export interface Thread {
  thread_id: string;
  title: string;
}
