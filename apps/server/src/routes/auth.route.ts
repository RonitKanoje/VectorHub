import express from "express";
import * as registerController from "../controllers/auth/register.controller.js";
import * as loginController from "../controllers/auth/login.controller.js";
import * as oauthController from "../controllers/auth/oauth.controller.js";
import {
  registerLimiter,
  verifyOtpLimiter,
  loginLimiter,
  refreshTokenLimiter,
  googleAuthLimiter
} from "../rate-limit/auth.rate-limit.js";

const router = express.Router();

router.post("/register", registerLimiter, registerController.register);
router.post("/verify", verifyOtpLimiter, registerController.verifyEmail);
router.post("/login", loginLimiter, loginController.login);
router.get("/logout", loginController.logout);
router.get("/logoutAll", loginController.logoutAll);
router.post("/refresh-token", refreshTokenLimiter, loginController.refreshToken);
router.get("/google", googleAuthLimiter, oauthController.googleLoginPage);
router.get("/google/callback", googleAuthLimiter, oauthController.getGoogleLoginCallBack);

export default router;
