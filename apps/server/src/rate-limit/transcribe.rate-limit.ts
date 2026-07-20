import { createRateLimiter } from "./create-rate-limiter.js";

export const transcribeLimiter = createRateLimiter({
    windowMs: 60 * 1000, // 1 minute
    max: 20,
    message: "Too many transcription requests. Please wait a moment.",
});
