import mongoose, { Document, Model, Schema } from "mongoose";

export interface IAccount extends Document {
  provider: string;
  providerAccountId: string;
  userId: mongoose.Types.ObjectId;
}

const accountSchema = new Schema<IAccount>(
  {
    provider: { type: String, required: true },
    providerAccountId: { type: String, required: true },
    userId: { type: Schema.Types.ObjectId, ref: "User", required: true },
  },
  { timestamps: true },
);

const Account: Model<IAccount> = mongoose.model<IAccount>(
  "Account",
  accountSchema,
);

export default Account;
