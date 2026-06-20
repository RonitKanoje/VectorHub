import { WebSocketServer } from "ws";
import fs from "fs";
import os from "os";
import path from "path";
import Groq from "groq-sdk";
import dotenv from "dotenv";

dotenv.config();

export function initWebSocket(server) {
  const wss = new WebSocketServer({ server });
  
  // Try to initialize Groq
  let groq;
  try {
    groq = new Groq({ apiKey: process.env.GROQ_API_KEY });
  } catch (err) {
    console.error("Failed to initialize Groq. Check GROQ_API_KEY.", err);
  }

  wss.on("connection", (ws) => {
    let audioBuffer = Buffer.alloc(0);

    ws.on("message", async (message) => {
      if (typeof message === "string") {
        try {
          const data = JSON.parse(message);
          if (data.type === "STOP_RECORDING") {
            if (audioBuffer.length === 0) return;
            if (!groq) {
                ws.send(JSON.stringify({ type: "error", message: "Groq not configured" }));
                return;
            }

            const tempFilePath = path.join(os.tmpdir(), `audio-${Date.now()}.webm`);
            fs.writeFileSync(tempFilePath, audioBuffer);

            try {
              const transcription = await groq.audio.transcriptions.create({
                file: fs.createReadStream(tempFilePath),
                model: "whisper-large-v3",
                response_format: "json",
              });
              
              ws.send(JSON.stringify({ type: "transcript", text: transcription.text }));
            } catch (e) {
              console.error("Groq error", e);
              ws.send(JSON.stringify({ type: "error", message: "Transcription failed" }));
            } finally {
              fs.unlinkSync(tempFilePath);
            }
            audioBuffer = Buffer.alloc(0);
          }
        } catch (e) {
          // If it's not JSON, ignore
        }
      } else {
        audioBuffer = Buffer.concat([audioBuffer, message]);
      }
    });

    ws.on("close", () => {
      audioBuffer = Buffer.alloc(0);
    });
  });

  return wss;
}
