import express from "express";
import * as registerController from "../controllers/auth/register.controller.js";
import * as loginController from "../controllers/auth/login.controller.js";
import * as oauthController from "../controllers/auth/oauth.controller.js";

const router = express.Router();

router.post("/register", registerController.register);
router.post("/verify", registerController.verifyEmail);
router.post("/login", loginController.login);
router.get("/logout", loginController.logout);
router.get("/logoutAll", loginController.logoutAll);
router.post("/refresh-token", loginController.refreshToken);
router.get("/google", oauthController.googleLoginPage);
router.get("/google/callback", oauthController.getGoogleLoginCallBack);

export default router;
