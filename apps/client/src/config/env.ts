function trimTrailingSlash(value: string): string {
  return value.replace(/\/+$/, "");
}

const rawApiBaseUrl = import.meta.env.VITE_API_BASE_URL;

if (rawApiBaseUrl === undefined || rawApiBaseUrl === null) {
  throw new Error("VITE_API_BASE_URL is not defined");
}

function toWebSocketUrl(baseUrl: string): string {
  const url = new URL(baseUrl, window.location.origin);
  url.protocol = url.protocol === "https:" ? "wss:" : "ws:";
  url.pathname = "/ws";
  url.search = "";
  url.hash = "";

  return trimTrailingSlash(url.toString());
}

export const API_BASE_URL = trimTrailingSlash(rawApiBaseUrl);
export const GOOGLE_AUTH_URL = `${API_BASE_URL}/api/auth/google`;
export const WEBSOCKET_BASE_URL = toWebSocketUrl(API_BASE_URL);
