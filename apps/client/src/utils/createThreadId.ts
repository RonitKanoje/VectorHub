// Some browsers (older Safari, some mobile) don't support crypto.randomUUID
export function createThreadId(): string {
  if ("randomUUID" in crypto) {
    return crypto.randomUUID();
  }
  return `local-${Date.now()}`;
}
