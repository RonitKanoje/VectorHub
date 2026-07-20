import { createRateLimiter } from "./create-rate-limiter.js";

export const aiChatLimiter = createRateLimiter({
    windowMs: 15 * 60 * 1000, // 15 minutes
    max: 50,
    message: "Too many AI chat requests. Please slow down and try again later.",
});

export const aiNamingLimiter = createRateLimiter({
    windowMs: 15 * 60 * 1000, // 15 minutes
    max: 50,
    message: "Too many naming operations. Please try again later.",
});

export const aiPollingLimiter = createRateLimiter({
    windowMs: 60 * 1000, // 1 minute
    max: 60,
    message: "Too many status checks. Polling limit exceeded.",
});

export const aiReadLimiter = createRateLimiter({
    windowMs: 60 * 1000, // 1 minute
    max: 100,
    message: "Too many read requests. Please try again later.",
});
