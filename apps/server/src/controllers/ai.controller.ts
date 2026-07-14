import { Request, Response } from "express";
import {
  forwardToThreadCore,
  forwardStreamToThreadCore,
} from "../utils/threadcore.js";

interface ChatBody {
  content?: string;
  thread_id?: string;
  role?: string;
  message?: string;
  is_tool_approval?: boolean | string;
}

export async function getThreads(req: Request, res: Response) {
  const mode = req.query.mode || "chat";
  return forwardToThreadCore(req, res, `/threads?mode=${mode}`);
}

export async function loadConversation(req: Request, res: Response) {
  return forwardToThreadCore(req, res, `/loadConv/${req.params.threadId}`);
}

export async function loadAnalystConversation(req: Request, res: Response) {
  return forwardToThreadCore(
    req,
    res,
    `/load_analyst_conv/${req.params.threadId}`,
  );
}

export async function getIngestionStatus(req: Request, res: Response) {
  return forwardToThreadCore(
    req,
    res,
    `/ingestion_status/${req.params.threadId}`,
  );
}

export async function getThreadStatus(req: Request, res: Response) {
  return forwardToThreadCore(req, res, `/thread_status/${req.params.threadId}`);
}

export async function chat(req: Request<{}, {}, ChatBody>, res: Response) {
  try {
    return await forwardStreamToThreadCore(req, res, "/chat", {
      method: "POST",
      body: buildChatPayload(req.body),
    });
  } catch (error) {
    const message =
      error instanceof Error ? error.message : "Invalid chat payload";
    return res.status(400).json({
      success: false,
      message,
    });
  }
}

export async function analystChat(
  req: Request<{}, {}, ChatBody>,
  res: Response,
) {
  try {
    return await forwardStreamToThreadCore(req, res, "/analyst_chat", {
      method: "POST",
      body: {
        message: req.body.message,
        thread_id: req.body.thread_id,
      },
    });
  } catch (error) {
    const message =
      error instanceof Error ? error.message : "Invalid analyst chat payload";
    return res.status(400).json({
      success: false,
      message,
    });
  }
}

export async function nameChat(req: Request, res: Response) {
  return forwardToThreadCore(req, res, "/nameChat", {
    method: "POST",
    body: req.body,
  });
}

export async function nameThreadFromUpload(req: Request, res: Response) {
  return forwardToThreadCore(req, res, "/nameThreadFromUpload", {
    method: "POST",
    body: req.body,
  });
}

function buildChatPayload(body: ChatBody = {}) {
  const content = body.content;
  const threadId = body.thread_id;
  const isToolApproval =
    body.is_tool_approval === true || body.is_tool_approval === "true";

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
    is_tool_approval: isToolApproval,
  };
}
