import { Groq } from "groq-sdk";
import multer from "multer";
import { requireAuth } from "../middlewares/auth.middleware.js";
import express from "express";

const groq = new Groq({ apiKey: process.env.GROQ_API_KEY });
const upload = multer({ storage: multer.memoryStorage() });
const router = express.Router();

router.use(requireAuth);

router.post("/transcribe", upload.single("audio"), async (req, res) => {
  try {
    if (!req.file) {
      return res.status(400).json({ error: "No audio file provided" });
    }

    // Convert buffer to a File-like object for Groq SDK
    const audioFile = new File([req.file.buffer], "recording.webm", {
      type: req.file.mimetype || "audio/webm",
    });

    const transcription = await groq.audio.transcriptions.create({
      file: audioFile,
      model: "whisper-large-v3-turbo",
      response_format: "json",
      language: "en",
    });

    return res.json({ text: transcription.text });
  } catch (error) {
    console.error("Transcription error:", error);
    return res.status(500).json({ error: "Transcription failed", detail: error.message });
  }
});

export default router;
