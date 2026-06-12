import fs from "node:fs/promises"; // importing file system 
import path from "node:path";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url); // current file path
const __dirname = path.dirname(__filename); // dir of __filename 
const uploadRoot = path.resolve(__dirname, "../../../../data/runtime/uploads");

export async function persistBase64File(file, userId, threadId) {
  const safeName = path.basename(file.name).replace(/[^\w.-]/g, "_"); // take out basename of file and replacing all weird characters with '_'
  const uploadDir = path.join(uploadRoot, String(userId), String(threadId));
  const contentBase64 = String(file.contentBase64).replace(
    /^data:.*;base64,/,
    "",
  );
  const buffer = Buffer.from(contentBase64, "base64"); // got original bytes 

  await fs.mkdir(uploadDir, { recursive: true }); // creating the folder 
  const outputPath = path.join(uploadDir, safeName);
  await fs.writeFile(outputPath, buffer); // storing the video on backend 
  return outputPath;
}