import { NextFunction, Request, Response } from "express";
import jwt from "jsonwebtoken";
import config from "../config/config.js";

interface JwtPayload extends jwt.JwtPayload {
  userId?: string;
}

export function requireAuth(req: Request, res: Response, next: NextFunction) {
  const authHeader = req.get("Authorization") || "";
  const [scheme, token] = authHeader.split(" ");

  if (scheme !== "Bearer" || !token) {
    return res.status(401).json({
      success: false,
      message: "Access token required",
    });
  }

  try {
    const decoded = jwt.verify(token, config.JWT_SECRET) as JwtPayload;
    req.userId = decoded.userId;
    return next();
  } catch {
    return res.status(401).json({
      success: false,
      message: "Access token expired or invalid",
    });
  }
}
