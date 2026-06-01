import mongoose from "mongoose";

const otpSchema = new mongoose.Schema(
  {
    email: {
      type: String,
      required: [true, "Email is required"],
      index: true,
    },
    user: {
      type: mongoose.Schema.Types.ObjectId,
      ref: "User",
      required: [true, "User is required"],
    },
    otpHash: {
      type: String,
      required: [true, "OTP hash is required"],
    },
  },
  {
    timestamps: true,
  },
);

// expire OTP documents after 10 minutes
otpSchema.index({ createdAt: 1 }, { expireAfterSeconds: 600 });

const Otp = mongoose.model("Otp", otpSchema);

export default Otp;
