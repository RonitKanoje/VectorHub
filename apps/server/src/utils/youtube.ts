export function normalizeYoutubeInput(input: unknown): string {
  const value = String(input).trim();

  try {
    const url = new URL(value);
    const videoId = url.searchParams.get("v");

    if (videoId) return videoId;

    const shortId = url.pathname.split("/").filter(Boolean).pop(); // remove the empty string => .filter(Boolea)
    return shortId || value;
  } catch {
    return value;
  }
}
