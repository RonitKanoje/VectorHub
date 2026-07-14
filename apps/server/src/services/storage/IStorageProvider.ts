import { Express } from "express";

export abstract class IStorageProvider {
  abstract saveFile(
    file: Express.Multer.File,
    userId: string,
    threadId: string,
  ): Promise<string>;
}
