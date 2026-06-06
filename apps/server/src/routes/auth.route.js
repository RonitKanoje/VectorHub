import express from "express";
import * as authController from "../controllers/auth.controller.js";

const router = express.Router();

/**
 * - route POST /api/auth/register
 */
router.post("/register", authController.register);

/**
 * - route POST /api/auth/verifyEmail
 */

router.post("/verify", authController.verifyEmail);

/**
 * - router POST /api/auth/login
 */
router.post("/login", authController.login);

/**
 * - router GET /api/auth/logout
 */
router.get("/logout", authController.logout);

/**
 * -
 *- router GET /api/auth/logoutAll
 */

router.get("/logoutAll", authController.logoutAll);

/**
 * - router GET /api/auth/refresh-token
 */

router.get("/refresh-token", authController.refreshToken);

router.get("/google", authController.googleLoginPage);

router.get("/google/callback", authController.getGoogleLoginCallBack);

export default router;
