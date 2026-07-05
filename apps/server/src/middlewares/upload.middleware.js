import multer from "multer";
import path from "path";
import fs from "fs";

const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    const userId = req.userId || "anonymous";
    const threadId = req.body.thread_id || "default_thread";

    // Path: data/runtime/uploads/<user_id>/<thread_id>
    const destDir = path.resolve(
      process.cwd(),
      "data",
      "runtime",
      "uploads",
      userId,
      threadId,
    ); // at the time of deployment er have to look here

    fs.mkdirSync(destDir, { recursive: true });
    cb(null, destDir);
  },
  filename: (req, file, cb) => {
    const uniqueSuffix = Date.now() + "-" + Math.round(Math.random() * 1e9);
    const ext = path.extname(file.originalname);
    cb(null, `${file.fieldname}-${uniqueSuffix}${ext}`);
  },
});

const fileFilter = (req, file, cb) => {
  const ext = path.extname(file.originalname).toLowerCase();

  // Reject specific executables
  if ([".exe", ".dll", ".bat"].includes(ext)) {
    return cb(new Error("Executable files are not allowed"), false);
  }

  // Validate allowed extensions
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
    cb(new Error(`Unsupported file type: ${ext}`), false);
  }
};

// multer configuration with file size limit
export const upload = multer({
  storage,
  fileFilter,
  limits: {
    fileSize: 50 * 1024 * 1024, // 50MB
  },
});
