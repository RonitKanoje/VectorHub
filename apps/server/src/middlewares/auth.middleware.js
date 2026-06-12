import jwt from "jsonwebtoken";
import config from "../config/config.js";

export function requireAuth(req, res, next) {
  const authHeader = req.get("Authorization") || ""; // stores 
  const [scheme, token] = authHeader.split(" ");

  if (scheme !== "Bearer" || !token) {
    return res.status(401).json({
      success: false,
      message: "Access token required",
    });
  }

  try {
    const decoded = jwt.verify(token, config.JWT_SECRET);
    req.userId = decoded.userId;
    return next();
  } catch (error) {
    return res.status(401).json({
      success: false,
      message: "Access token expired or invalid",
    });
  }
}
