import express from "express";
import { requireAuth } from "../middlewares/auth.middleware.js";
import {
  getThreads,
  loadConversation,
  loadAnalystConversation,
  getIngestionStatus,
  getThreadStatus,
  chat,
  nameChat,
  nameThreadFromUpload,
  analystChat,
} from "../controllers/ai.controller.js";
import {
  aiChatLimiter,
  aiNamingLimiter,
  aiPollingLimiter,
  aiReadLimiter,
} from "../rate-limit/ai.rate-limit.js";

const router = express.Router();

router.use(requireAuth);

router.get("/threads", aiReadLimiter, getThreads);
router.get("/loadConv/:threadId", aiReadLimiter, loadConversation);
router.get("/load_analyst_conv/:threadId", aiReadLimiter, loadAnalystConversation);
router.get("/ingestion_status/:threadId", aiPollingLimiter, getIngestionStatus);
router.get("/thread_status/:threadId", aiPollingLimiter, getThreadStatus);
router.post("/chat", aiChatLimiter, chat);
router.post("/nameChat", aiNamingLimiter, nameChat);
router.post("/nameThreadFromUpload", aiNamingLimiter, nameThreadFromUpload);
router.post("/analyst_chat", aiChatLimiter, analystChat);

export default router;
