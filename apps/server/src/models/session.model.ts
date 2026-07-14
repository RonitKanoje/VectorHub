import mongoose, { Document, Model, Schema } from "mongoose";

export interface ISession extends Document {
  user: mongoose.Types.ObjectId;
  refreshTokenHash: string;
  ip: string;
  userAgent: string;
  revoked: boolean;
}

const sessionSchema = new Schema<ISession>(
  {
    user: {
      type: Schema.Types.ObjectId,
      ref: "User",
      required: [true, "User is required"],
    },
    refreshTokenHash: {
      type: String,
      required: [true, "Refresh token hash is required"],
    },
    ip: {
      type: String,
      required: [true, "IP address is required"],
    },
    userAgent: {
      type: String,
      required: [true, "User agent is required"],
    },
    revoked: {
      type: Boolean,
      default: false,
    },
  },
  {
    timestamps: true,
  },
);

const Session: Model<ISession> = mongoose.model<ISession>(
  "Session",
  sessionSchema,
);

export default Session;
