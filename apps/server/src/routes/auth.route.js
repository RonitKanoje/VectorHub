import express from "express";
import * as registerController from "../controllers/auth/register.controller.js";
import * as loginController from "../controllers/auth/login.controller.js";
import * as oauthController from "../controllers/auth/oauth.controller.js";

const router = express.Router();

/**
 * - route POST /api/auth/register
 */
router.post("/register", registerController.register);

/**
 * - route POST /api/auth/verify
 */

router.post("/verify", registerController.verifyEmail);

/**
 * - router POST /api/auth/login
 */
router.post("/login", loginController.login);

/**
 * - router GET /api/auth/logout
 */
router.get("/logout", loginController.logout);

/**
 * -
 *- router GET /api/auth/logoutAll
 */

router.get("/logoutAll", loginController.logoutAll);

/**
 * - router GET /api/auth/refresh-token
 */

router.post("/refresh-token", loginController.refreshToken);

router.get("/google", oauthController.googleLoginPage);

router.get("/google/callback", oauthController.getGoogleLoginCallBack);

export default router;
