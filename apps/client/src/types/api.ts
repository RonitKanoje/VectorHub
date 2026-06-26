// ─── API error types ──────────────────────────────────────────────────────────

/** A single field-level validation error returned by FastAPI. */
export interface ApiErrorDetail {
  loc?: Array<string | number>;
  msg?: string;
}

/** The JSON body of an API error response. */
export interface ApiError {
  message?: string;
  detail?: string | ApiErrorDetail[];
}

/** Structurally-typed wrapper used to safely extract error info from `unknown`. */
export interface ApiErrorLike {
  response?: {
    data?: ApiError;
  };
}
