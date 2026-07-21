import { createRateLimiter } from "./create-rate-limiter.js";

export const loginLimiter = createRateLimiter({
  windowMs: 15 * 60 * 1000,
  max: 3,
  message: "Too many login attempts. Please try again after 15 minutes.",
  prefix: "login",
});

export const registerLimiter = createRateLimiter({
  windowMs: 60 * 60 * 1000,
  max: 3,
  message: "Too many registration attempts. Please try again after an hour.",
  prefix: "register",
});

export const verifyOtpLimiter = createRateLimiter({
  windowMs: 15 * 60 * 1000,
  max: 10,
  message: "Too many OTP verification attempts. Please try again later.",
  prefix: "verify-otp",
});

export const refreshTokenLimiter = createRateLimiter({
  windowMs: 15 * 60 * 1000,
  max: 30,
  message: "Too many refresh token requests. Please try again later.",
  prefix: "refresh-token",
});

export const googleAuthLimiter = createRateLimiter({
  windowMs: 15 * 60 * 1000,
  max: 10,
  message: "Too many Google authentication attempts. Please try again later.",
  prefix: "google-auth",
});
