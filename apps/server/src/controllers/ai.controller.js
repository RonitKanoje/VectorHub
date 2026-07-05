import { normalizeYoutubeInput } from "../utils/youtube.js";
import {
  forwardToThreadCore,
  forwardStreamToThreadCore,
} from "../utils/threadcore.js";

export async function getThreads(req, res) {
  const mode = req.query.mode || "chat";
  return forwardToThreadCore(req, res, `/threads?mode=${mode}`);
}

export async function loadConversation(req, res) {
  return forwardToThreadCore(req, res, `/loadConv/${req.params.threadId}`);
}

export async function loadAnalystConversation(req, res) {
  return forwardToThreadCore(
    req,
    res,
    `/load_analyst_conv/${req.params.threadId}`,
  );
}

export async function getIngestionStatus(req, res) {
  return forwardToThreadCore(
    req,
    res,
    `/ingestion_status/${req.params.threadId}`,
  );
}

export async function getThreadStatus(req, res) {
  return forwardToThreadCore(req, res, `/thread_status/${req.params.threadId}`);
}

export async function chat(req, res) {
  try {
    return await forwardStreamToThreadCore(req, res, "/chat", {
      method: "POST",
      body: buildChatPayload(req.body),
    });
  } catch (error) {
    return res.status(400).json({
      success: false,
      message: error.message || "Invalid chat payload",
    });
  }
}

export async function analystChat(req, res) {
  try {
    return await forwardStreamToThreadCore(req, res, "/analyst_chat", {
      method: "POST",
      body: {
        message: req.body.message,
        thread_id: req.body.thread_id,
      },
    });
  } catch (error) {
    return res.status(400).json({
      success: false,
      message: error.message || "Invalid analyst chat payload",
    });
  }
}

export async function nameChat(req, res) {
  return forwardToThreadCore(req, res, "/nameChat", {
    method: "POST",
    body: req.body,
  });
}

export async function nameThreadFromUpload(req, res) {
  return forwardToThreadCore(req, res, "/nameThreadFromUpload", {
    method: "POST",
    body: req.body,
  });
}

function buildChatPayload(body = {}) {
  const content = body.content;
  const threadId = body.thread_id;

  if (!content || String(content).trim() === "") {
    throw new Error("message content is required");
  }

  if (!threadId || String(threadId).trim() === "") {
    throw new Error("thread_id is required");
  }

  return {
    role: body.role || "user",
    content: String(content).trim(),
    thread_id: String(threadId).trim(),
  };
}
