import { WebSocketServer } from "ws";
import fs from "fs";
import fsPromises from "fs/promises";
import os from "os";
import path from "path";
import Groq from "groq-sdk";
import dotenv from "dotenv";

dotenv.config();

export function initWebSocket(server) {
  const wss = new WebSocketServer({ server });

  let groq;
  try {
    groq = new Groq({ apiKey: process.env.GROQ_API_KEY });
  } catch (err) {
    console.error("Failed to initialize Groq. Check GROQ_API_KEY.", err);
  }

  wss.on("connection", (ws) => {
    let isStopped = false;
    let inFlightCount = 0;

    // Transcribes ONE complete, independent WebM segment. No merging, no
    // sliding window, no shared header chunk — every segment sent by the
    // client is already a fully self-contained, decodable audio file.
    async function transcribeSegment(buffer) {
      inFlightCount++;

      if (!groq) {
        ws.send(
          JSON.stringify({ type: "error", message: "Groq not configured" }),
        );
        inFlightCount--;
        return;
      }

      const tempFilePath = path.join(
        os.tmpdir(),
        `audio-${Date.now()}-${Math.random().toString(36).slice(2)}.webm`,
      );

      try {
        await fsPromises.writeFile(tempFilePath, buffer);

        const transcription = await groq.audio.transcriptions.create({
          file: fs.createReadStream(tempFilePath),
          model: "whisper-large-v3",
          response_format: "json",
          language: "en",
        });

        ws.send(
          JSON.stringify({
            // isStopped is checked here, after the await, not at call time.
            // STOP_RECORDING is a tiny control message that's processed
            // near-instantly, while this transcription call is a real
            // network round trip — so by the time we get here, isStopped
            // correctly reflects whether this was the last segment.
            type: isStopped ? "final_transcript" : "partial_transcript",
            text: transcription.text,
          }),
        );
      } catch (err) {
        console.error("Groq transcription error", err);
        ws.send(
          JSON.stringify({ type: "error", message: "Transcription failed" }),
        );
      } finally {
        inFlightCount--;
        fsPromises.unlink(tempFilePath).catch(() => {});
      }
    }

    ws.on("message", async (message) => {
      if (typeof message === "string") {
        try {
          const data = JSON.parse(message);
          if (data.type === "STOP_RECORDING") {
            isStopped = true;
            // If nothing is currently being transcribed, there's no result
            // left to report — reply immediately so the client doesn't sit
            // waiting for a final_transcript that would otherwise never come.
            if (inFlightCount === 0) {
              ws.send(JSON.stringify({ type: "final_transcript", text: "" }));
            }
          }
        } catch {
          // Ignore malformed control messages.
        }
        return;
      }

      // Binary message: one complete WebM Blob for a single 3-second segment.
      await transcribeSegment(message);
    });

    ws.on("close", () => {
      isStopped = true;
    });
  });

  return wss;
}
