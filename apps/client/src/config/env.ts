function trimTrailingSlash(value: string): string {
  return value.replace(/\/+$/, "");
}

function getRequiredEnv(name: string): string {
  const value = import.meta.env[name];

  if (!value) {
    throw new Error(`${name} is not defined`);
  }

  return trimTrailingSlash(value);
}

function toWebSocketUrl(baseUrl: string): string {
  const url = new URL(baseUrl, window.location.origin);
  url.protocol = url.protocol === "https:" ? "wss:" : "ws:";
  url.pathname = "";
  url.search = "";
  url.hash = "";

  return trimTrailingSlash(url.toString());
}

export const API_BASE_URL = getRequiredEnv("VITE_API_BASE_URL");
export const GOOGLE_AUTH_URL = `${API_BASE_URL}/api/auth/google`;
export const WEBSOCKET_BASE_URL = toWebSocketUrl(API_BASE_URL);
