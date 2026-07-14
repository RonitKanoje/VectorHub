import mongoose, { Document, Model, Schema } from "mongoose";

export interface IVerificationToken extends Document {
  user: mongoose.Types.ObjectId;
  otpHash: string;
  verificationToken: string;
  expiresAt: Date;
}

const verificationTokenSchema = new Schema<IVerificationToken>(
  {
    user: { type: Schema.Types.ObjectId, ref: "User", required: true },
    otpHash: { type: String, required: true },
    verificationToken: { type: String, required: true },
    expiresAt: { type: Date, required: true },
  },
  { timestamps: true },
);

const VerificationToken: Model<IVerificationToken> =
  mongoose.model<IVerificationToken>(
    "VerificationToken",
    verificationTokenSchema,
  );

export default VerificationToken;
