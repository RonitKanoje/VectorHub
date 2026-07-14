import mongoose, { Document, Model, Schema } from "mongoose";

export interface IOtp extends Document {
  email: string;
  user: mongoose.Types.ObjectId;
  otpHash: string;
}

const otpSchema = new Schema<IOtp>(
  {
    email: { type: String, required: true },
    user: { type: Schema.Types.ObjectId, ref: "User", required: true },
    otpHash: { type: String, required: true },
  },
  { timestamps: true },
);

const Otp: Model<IOtp> = mongoose.model<IOtp>("Otp", otpSchema);

export default Otp;
