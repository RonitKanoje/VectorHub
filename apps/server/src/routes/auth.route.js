import express from "express";
import * as authController from "../controllers/auth.controller.js";

const router = express.Router();

/**
 * - route POST /api/auth/register
 */

router.post("/register", authController.register);

export default router;
