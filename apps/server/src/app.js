import express from "express";
import authRouter from "./routes/auth.route.js";
import cors from "cors";
import { parseCookies } from "./middlewares/cookie.middleware.js";

const app = express();

app.use(
  cors({
    origin: "http://localhost:5173",
    credentials: true,
  }),
);

app.use(parseCookies);
app.use(express.json());

app.use("/api/auth", authRouter);

export default app;
