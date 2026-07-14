import mongoose, { Document, Model, Schema } from "mongoose";

export interface IUploadedFile extends Document {
  user_id?: string;
  thread_id?: string;
  original_filename?: string;
  stored_filename?: string;
  file_path?: string;
  mime_type?: string;
  file_size?: number;
  status?: string;
}

const uploadedFileSchema = new Schema<IUploadedFile>(
  {
    user_id: { type: String },
    thread_id: { type: String },
    original_filename: { type: String },
    stored_filename: { type: String },
    file_path: { type: String },
    mime_type: { type: String },
    file_size: { type: Number },
    status: { type: String },
  },
  { timestamps: true },
);

const UploadedFile: Model<IUploadedFile> = mongoose.model<IUploadedFile>(
  "UploadedFile",
  uploadedFileSchema,
);

export default UploadedFile;
