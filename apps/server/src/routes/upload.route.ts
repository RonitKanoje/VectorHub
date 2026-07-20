import express from "express";
import { uploadMedia } from "../controllers/upload.controller.js";
import { upload } from "../middlewares/upload.middleware.js";
import { requireAuth } from "../middlewares/auth.middleware.js";
import { fileUploadLimiter } from "../rate-limit/upload.rate-limit.js";

const router = express.Router();

router.post("/", requireAuth, fileUploadLimiter, upload.single("file"), uploadMedia);

export default router;
