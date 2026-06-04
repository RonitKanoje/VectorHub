import mongoose from "mongoose";

const verificationSchema = new mongoose.Schema(
  {
    user: {
      type: mongoose.Schema.Types.ObjectId,
      ref: "User",
      required: true,
    },

    otpHash: {
      type: String,
      required: true,
    },

    verificationToken: {
      type: String,
      required: true,
      unique: true,
    },

    expiresAt: {
      type: Date,
      required: true,
    },
  },
  {
    timestamps: true,
  },
);

verificationSchema.index({ expiresAt: 1 }, { expireAfterSeconds: 0 });

const verificationToken = mongoose.model(
  "VerificationToken",
  verificationSchema,
);

export default verificationToken;
