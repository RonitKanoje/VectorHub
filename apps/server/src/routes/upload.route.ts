import express from "express";
import { uploadMedia } from "../controllers/upload.controller.js";
import { upload } from "../middlewares/upload.middleware.js";
import { requireAuth } from "../middlewares/auth.middleware.js";

const router = express.Router();

router.post("/", requireAuth, upload.single("file"), uploadMedia);

export default router;
