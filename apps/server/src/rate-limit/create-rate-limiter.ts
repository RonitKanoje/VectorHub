import rateLimit from "express-rate-limit";
import { createRedisStore } from "./store.js";

interface RateLimiterOptions {
  windowMs: number;
  max: number;
  message: string;
  prefix: string;
}

export function createRateLimiter({
  windowMs,
  max,
  message,
  prefix,
}: RateLimiterOptions) {
  return rateLimit({
    windowMs,
    max,

    store: createRedisStore(prefix),

    standardHeaders: true,
    legacyHeaders: false,

    message: {
      success: false,
      message,
    },
  });
}
