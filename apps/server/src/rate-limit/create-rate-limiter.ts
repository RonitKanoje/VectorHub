import rateLimit from "express-rate-limit";
import { redisStore } from "./store.js";

interface RateLimiterOptions {
    windowMs: number;
    max: number;
    message: string;
}

export function createRateLimiter({
    windowMs,
    max,
    message,
}: RateLimiterOptions) {
    return rateLimit({
        windowMs,
        max,

        store: redisStore,

        standardHeaders: true,
        legacyHeaders: false,

        message: {
            success: false,
            message,
        },
    });
}