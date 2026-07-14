import "./env.js";

const requiredEnvVars = [
  "MONGODB_COMPASS_URL",
  "JWT_SECRET",
  "GOOGLE_USER",
  "GOOGLE_CLIENT_ID",
  "GOOGLE_CLIENT_SECRET",
  "GOOGLE_REFRESH_TOKEN",
  "GOOGLE_CONTINUE_WITH_GOOGLE_CLIENT_SECRET",
  "GOOGLE_CONTINUE_WITH_GOOGLE_CLIENT_ID",
] as const;

for (const envVar of requiredEnvVars) {
  if (!process.env[envVar]) {
    throw new Error(`${envVar} is not defined in .env file`);
  }
}

const config = {
  MONGODB_COMPASS_URL: process.env.MONGODB_COMPASS_URL!,
  JWT_SECRET: process.env.JWT_SECRET!,
  GOOGLE_USER: process.env.GOOGLE_USER!,
  GOOGLE_CLIENT_ID: process.env.GOOGLE_CLIENT_ID!,
  GOOGLE_CLIENT_SECRET: process.env.GOOGLE_CLIENT_SECRET!,
  GOOGLE_REFRESH_TOKEN: process.env.GOOGLE_REFRESH_TOKEN!,
  GOOGLE_CWT_CLIENT_SECRET:
    process.env.GOOGLE_CONTINUE_WITH_GOOGLE_CLIENT_SECRET!,
  GOOGLE_CWT_CLIENT_ID: process.env.GOOGLE_CONTINUE_WITH_GOOGLE_CLIENT_ID!,
  CLIENT_URL: process.env.CLIENT_URL,
  THREADCORE_URL: process.env.THREADCORE_URL,
  NODE_ENV: process.env.NODE_ENV,
  PORT: process.env.PORT,
} as const;

export default config;
