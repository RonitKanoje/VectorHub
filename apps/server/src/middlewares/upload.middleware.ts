import multer from "multer";
import path from "path";
import fs from "fs";
import { Request } from "express";

const storage = multer.diskStorage({
  destination: (
    req: Request,
    file: Express.Multer.File,
    cb: (error: Error | null, destination: string) => void,
  ) => {
    const userId = req.userId || "anonymous";
    const threadId = req.body.thread_id || "default_thread";

    const destDir = path.resolve(
      process.cwd(),
      "data",
      "runtime",
      "uploads",
      userId,
      threadId,
    );

    fs.mkdirSync(destDir, { recursive: true });
    cb(null, destDir);
  },

  filename: (
    req: Request,
    file: Express.Multer.File,
    cb: (error: Error | null, filename: string) => void,
  ) => {
    const uniqueSuffix = Date.now() + "-" + Math.round(Math.random() * 1e9);
    const ext = path.extname(file.originalname);

    cb(null, `${file.fieldname}-${uniqueSuffix}${ext}`);
  },
});

const fileFilter = (
  req: Request,
  file: Express.Multer.File,
  cb: multer.FileFilterCallback,
) => {
  const ext = path.extname(file.originalname).toLowerCase();

  if ([".exe", ".dll", ".bat"].includes(ext)) {
    return cb(new Error("Executable files are not allowed"));
  }

  const allowedExtensions = [
    ".pdf",
    ".txt",
    ".mp3",
    ".mp4",
    ".docx",
    ".webm",
    ".csv",
    ".xlsx",
  ];

  if (allowedExtensions.includes(ext)) {
    cb(null, true);
  } else {
    cb(new Error(`Unsupported file type: ${ext}`));
  }
};

export const upload = multer({
  storage,
  fileFilter,
  limits: {
    fileSize: 50 * 1024 * 1024,
  },
});