import mongoose from "mongoose";
import config from "./config.js";

const connectDB = async () => {
  await mongoose.connect(config.MONGODB_COMPASS_URL);

  console.log("MongoDB Connected");
};

export default connectDB;
