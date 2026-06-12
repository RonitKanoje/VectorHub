import express from "express";
import cors from "cors";
import cookieParser from "cookie-parser";

import authRouter from "./routes/auth.route.js";
import aiRouter from "./routes/ai.route.js";
import config from "./config/config.js";
const app = express();

app.use(
  cors({
    origin: config.CLIENT_URL,
    credentials: true,
  }),
);

app.use(express.json({ limit: "100mb" }));
app.use(express.urlencoded({ extended: true, limit: "100mb" }));

app.use(cookieParser());

app.use("/api/auth", authRouter);
app.use("/api/ai", aiRouter);

export default app;
