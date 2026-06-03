import dotenv from "dotenv";

dotenv.config();

const requiredEnvVars = [
  "MONGODB_COMPASS_URL",
  "JWT_SECRET",
  "GOOGLE_USER",
  "GOOGLE_CLIENT_ID",
  "GOOGLE_CLIENT_SECRET",
  "GOOGLE_REFRESH_TOKEN",
];

for (const envVar of requiredEnvVars) {
  if (!process.env[envVar]) {
    throw new Error(`${envVar} is not defined in .env file`);
  }
}

const config = {
  MONGODB_COMPASS_URL: process.env.MONGODB_COMPASS_URL,

  JWT_SECRET: process.env.JWT_SECRET,

  GOOGLE_USER: process.env.GOOGLE_USER,
  GOOGLE_CLIENT_ID: process.env.GOOGLE_CLIENT_ID,
  GOOGLE_CLIENT_SECRET: process.env.GOOGLE_CLIENT_SECRET,
  GOOGLE_REFRESH_TOKEN: process.env.GOOGLE_REFRESH_TOKEN,

  PORT: process.env.PORT || 3000,
};

export default config;
