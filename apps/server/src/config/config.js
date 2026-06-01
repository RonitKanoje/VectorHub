import dotenv from "dotenv";

dotenv.config();

if (!process.env.MONGODB_COMPASS_URL) {
  throw new Error("MONGODB_URL is not defined in .env file");
}

const config = {
  MONGODB_COMPASS_URL: process.env.MONGODB_COMPASS_URL,
};
  
export default config;
