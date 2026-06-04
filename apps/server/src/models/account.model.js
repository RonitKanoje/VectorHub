import mongoose from "mongoose";

const accountSchema = new mongoose.Schema(
  {
    userId: {
      type: mongoose.Schema.Types.ObjectId,
      ref: "User",
      required: true,
      index: true,
    },

    provider: {
      type: String,
      required: true,
      enum: ["google", "github"],
    },

    providerAccountId: {
      // every email id has a unique providerAccountId
      type: String,
      required: true,
    },
  },
  {
    timestamps: true,
  },
);

// Prevent duplicate OAuth accounts
accountSchema.index(
  {
    provider: 1,
    providerAccountId: 1,
  },
  {
    unique: true,
  },
);

const Account = mongoose.model("Account", accountSchema);

export default Account;
