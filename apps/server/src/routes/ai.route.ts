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

const router = express.Router();

router.use(requireAuth);

router.get("/threads", getThreads);
router.get("/loadConv/:threadId", loadConversation);
router.get("/load_analyst_conv/:threadId", loadAnalystConversation);
router.get("/ingestion_status/:threadId", getIngestionStatus);
router.get("/thread_status/:threadId", getThreadStatus);
router.post("/chat", chat);
router.post("/nameChat", nameChat);
router.post("/nameThreadFromUpload", nameThreadFromUpload);
router.post("/analyst_chat", analystChat);

export default router;
