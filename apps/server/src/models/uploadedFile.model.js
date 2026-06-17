import mongoose from "mongoose";

const uploadedFileSchema = new mongoose.Schema(
  {
    user_id: { type: String, required: true },
    thread_id: { type: String, required: true },
    original_filename: { type: String, required: true },
    stored_filename: { type: String, required: true },
    file_path: { type: String, required: true },
    mime_type: { type: String, required: true },
    file_size: { type: Number, required: true },
    status: {
      type: String,
      enum: ["UPLOADED", "PROCESSING", "COMPLETED", "FAILED"],
      default: "UPLOADED",
    },
  },
  { timestamps: true }
);

const UploadedFile = mongoose.model("UploadedFile", uploadedFileSchema);

export default UploadedFile;
