import express from "express";
import { requireAuth } from "../middlewares/auth.middleware.js";
import {
  getThreads,
  loadConversation,
  getIngestionStatus,
  getThreadStatus,
  chat,
  nameChat,
  processMedia,
} from "../controllers/ai.controller.js";

const router = express.Router();

router.use(requireAuth); // middleware 

router.get("/threads", getThreads);
router.get("/loadConv/:threadId", loadConversation);
router.get("/ingestion_status/:threadId", getIngestionStatus);
router.get("/thread_status/:threadId", getThreadStatus);
router.post("/chat", chat);
router.post("/nameChat", nameChat);
router.post("/process_media", processMedia);

export default router;
