import { persistBase64File } from "../utils/fileUpload.js";
import { normalizeYoutubeInput } from "../utils/youtube.js";
import { forwardToThreadCore } from "../utils/threadcore.js";

export async function getThreads(req, res) {
  return forwardToThreadCore(req, res, "/threads");
}

export async function loadConversation(req, res) {
  return forwardToThreadCore(req, res, `/loadConv/${req.params.threadId}`);
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
    return await forwardToThreadCore(req, res, "/chat", {
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

export async function nameChat(req, res) {
  return forwardToThreadCore(req, res, "/nameChat", {
    method: "POST",
    body: req.body,
  });
}

export async function processMedia(req, res) {
  try {
    const payload = await buildProcessMediaPayload(req);
    return await forwardToThreadCore(req, res, "/process_media", {
      method: "POST",
      body: payload,
    });
  } catch (error) {
    return res.status(400).json({
      success: false,
      message: error.message || "Invalid media payload",
    });
  }
}

async function buildProcessMediaPayload(req) {
  const { media, thread_id, language, path: sourcePath, file } = req.body;

  if (!media || !thread_id) {
    throw new Error("media and thread_id are required");
  }

  if (file?.contentBase64 && file?.name) {
    return {
      media,
      thread_id,
      language: language || null,
      path: await persistBase64File(file, req.userId, thread_id),
    };
  }

  if (!sourcePath || String(sourcePath).trim() === "") {
    // checks whether user has provided url
    throw new Error("path is required when no file is uploaded");
  }

  return {
    media,
    thread_id,
    language: language || null,
    path: media === "youtube" ? normalizeYoutubeInput(sourcePath) : sourcePath,
  };
}

function buildChatPayload(body = {}) {
  const lastMessage = Array.isArray(body.messages)
    ? [...body.messages].reverse().find((item) => item?.role !== "assistant")
    : null; // user's last message

  const content =
    body.content ??
    body.message ??
    body.text ??
    body.query ??
    lastMessage?.content ??
    lastMessage?.message;

  const threadId = body.thread_id ?? body.threadId;

  if (!content || String(content).trim() === "") {
    throw new Error("message content is required");
  }
  if (!threadId || String(threadId).trim() === "") {
    throw new Error("thread_id is required");
  }

  return {
    role: body.role || lastMessage?.role || "user",
    content: String(content).trim(),
    thread_id: String(threadId).trim(),
  };
}
