import UploadedFile from "../models/uploadedFile.model.js";
import { localStorageProvider } from "../services/storage/localStorage.js";
import { forwardToThreadCore } from "../utils/threadcore.js";
import { normalizeYoutubeInput } from "../utils/youtube.js";

export async function uploadMedia(req, res) {
  try {
    const { file, userId } = req;
    const { thread_id, media, language } = req.body;

    if (!thread_id || !media) {
      return res.status(400).json({ success: false, message: "thread_id and media are required" });
    }

    let filePath;

    if (file) {
      // 1. Save file via abstract storage provider
      filePath = await localStorageProvider.saveFile(file, userId, thread_id);

      // 2. Store metadata in DB
      await UploadedFile.create({
        user_id: userId,
        thread_id: thread_id,
        original_filename: file.originalname,
        stored_filename: file.filename,
        file_path: filePath,
        mime_type: file.mimetype,
        file_size: file.size,
        status: "UPLOADED",
      });
    } else {
      // Fallback for youtube or raw text payloads
      filePath = media === "youtube" ? normalizeYoutubeInput(req.body.path) : req.body.path;
      if (!filePath) {
        return res.status(400).json({ success: false, message: "path or file is required" });
      }
    }

    // 3. Trigger FastAPI ingestion
    const payload = {
      media,
      thread_id,
      language: language || null,
      path: filePath,
    };

    const endpoint = media === "dataset" ? "/process_dataset" : "/process_media";

    return await forwardToThreadCore(req, res, endpoint, {
      method: "POST",
      body: payload,
    });

  } catch (error) {
    console.error("Upload error:", error);
    return res.status(500).json({
      success: false,
      message: error.message || "Failed to process upload",
    });
  }
}
