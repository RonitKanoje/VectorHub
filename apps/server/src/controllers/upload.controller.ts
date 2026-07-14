import { Request, Response } from "express";
import UploadedFile from "../models/uploadedFile.model.js";
import { localStorageProvider } from "../services/storage/localStorage.js";
import { forwardToThreadCore } from "../utils/threadcore.js";
import { normalizeYoutubeInput } from "../utils/youtube.js";

interface UploadBody {
  thread_id?: string;
  media?: string;
  language?: string;
  path?: string;
  document_name?: string;
}

export async function uploadMedia(
  req: Request<{}, {}, UploadBody>,
  res: Response,
) {
  try {
    const { file, userId } = req;
    const { thread_id, media, language } = req.body;

    if (!thread_id || !media) {
      return res
        .status(400)
        .json({ success: false, message: "thread_id and media are required" });
    }

    let filePath: string;

    if (file) {
      filePath = await localStorageProvider.saveFile(
        file,
        userId || "anonymous",
        thread_id,
      );

      await UploadedFile.create({
        user_id: userId,
        thread_id,
        original_filename: file.originalname,
        stored_filename: file.filename,
        file_path: filePath,
        mime_type: file.mimetype,
        file_size: file.size,
        status: "UPLOADED",
      });
    } else {
      filePath =
        media === "youtube"
          ? normalizeYoutubeInput(req.body.path)
          : req.body.path || "";
      if (!filePath) {
        return res
          .status(400)
          .json({ success: false, message: "path or file is required" });
      }
    }

    const payload = {
      media,
      thread_id,
      language: language || null,
      path: filePath,
      document_name: file ? file.originalname : req.body.document_name || null,
    };

    const endpoint =
      media === "dataset" ? "/process_dataset" : "/process_media";

    return await forwardToThreadCore(req, res, endpoint, {
      method: "POST",
      body: payload,
    });
  } catch (error) {
    const message =
      error instanceof Error ? error.message : "Failed to process upload";
    console.error("Upload error:", error);
    return res.status(500).json({
      success: false,
      message,
    });
  }
}
