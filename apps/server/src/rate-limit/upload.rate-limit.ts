import { createRateLimiter } from "./create-rate-limiter.js";

export const fileUploadLimiter = createRateLimiter({
  windowMs: 60 * 60 * 1000, // 1 hour
  max: 15,
  message: "Too many files uploaded. Please try again after an hour.",
  prefix: "file-upload",
});
