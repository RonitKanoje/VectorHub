import { IStorageProvider } from "./IStorageProvider.js";
import { Express } from "express";

export class LocalStorageProvider extends IStorageProvider {
  async saveFile(file: Express.Multer.File, userId: string, threadId: string) {
    if (!file || !file.path) {
      throw new Error("File not provided or not saved by Multer");
    }

    return file.path;
  }
}

export const localStorageProvider = new LocalStorageProvider();
