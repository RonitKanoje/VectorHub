import { IStorageProvider } from "./IStorageProvider.js";
import fs from "fs/promises";

export class LocalStorageProvider extends IStorageProvider {
  /**
   * Multer already saves the file to disk based on our middleware config.
   * This method just returns the absolute path so we can treat it abstractly.
   */
  async saveFile(file, userId, threadId) {
    if (!file || !file.path) {
      throw new Error("File not provided or not saved by Multer");
    }
    return file.path;
  }

  async deleteFile(filePath) {
    try {
      await fs.unlink(filePath);
    } catch (err) {
      if (err.code !== "ENOENT") {
        throw err;
      }
    }
  }
}

export const localStorageProvider = new LocalStorageProvider();
