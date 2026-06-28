import User from "../../models/user.model.js";
import Session from "../../models/session.model.js";
import bcrypt from "bcrypt";
import jwt from "jsonwebtoken";
import config from "../../config/config.js";
import { generateToken } from "../../utils/token.utils.js";

export async function login(req, res) {
  try {
    const { username, password } = req.body;

    if (!username) {
      return res.status(400).json({
        success: false,
        message: "Please enter your username",
      });
    }
    if (!password) {
      return res.status(400).json({
        success: false,
        message: "Please enter your password",
      });
    }

    // Space validations moved to client

    const user = await User.findOne({ username });

    if (!user) {
      return res.status(400).json({
        success: false,
        message: "Invalid username or password",
      });
    }

    if (!user.isVerified) {
      return res.status(400).json({
        success: false,
        message: "Email not verified",
      });
    }

    const isValidPassword = await bcrypt.compare(password, user.password);

    if (!isValidPassword) {
      return res.status(400).json({
        success: false,
        message: "Invalid password",
      });
    }

    const session = await Session.create({
      user: user._id,
      refreshTokenHash: "pending", // temporary value
      ip: req.ip,
      userAgent: req.get("User-Agent"),
    });

    const refreshToken = await generateToken(
      { userId: user._id, sessionId: session._id },
      "7d",
    );

    console.log({
      userId: user._id,
      username: user.username,
      email: user.email,
    });

    const accessToken = await generateToken(
      {
        userId: user._id,
        username: user.username,
        name: user.name,
        email: user.email,
      },
      "15m",
    );

    const refreshTokenHash = await bcrypt.hash(refreshToken, 10);
    session.refreshTokenHash = refreshTokenHash;
    await session.save();

    res.cookie("refreshToken", refreshToken, {
      httpOnly: true,
      sameSite: "strict",
      maxAge: 7 * 24 * 60 * 60 * 1000, // 7 days
    });

    return res.status(200).json({
      success: true,
      message: "Login successful",
      accessToken,
    });
  } catch (error) {
    console.error(error);
    return res.status(500).json({
      success: false,
      message: "Internal Server Error",
    });
  }
}

export async function refreshToken(req, res) {
  try {
    const { refreshToken } = req.cookies;

    if (!refreshToken) {
      return res.status(401).json({
        success: false,
        message: "Refresh token not found",
      });
    }

    const decoded = jwt.verify(refreshToken, process.env.JWT_SECRET);

    const session = await Session.findOne({
      user: decoded.userId,
      _id: decoded.sessionId,
      revoked: false,
    });

    if (!session) {
      return res.status(401).json({
        success: false,
        message: "Invalid refresh token",
      });
    }

    const isValid = await bcrypt.compare(
      refreshToken,
      session.refreshTokenHash,
    );

    if (!isValid) {
      return res.status(401).json({
        success: false,
        message: "Invalid refresh token",
      });
    }

    const accessToken = await generateToken(
      {
        userId: user._id,
        username: user.username,
        name: user.name,
        email: user.email,
      },
      "15m",
    );

    const newRefreshToken = await generateToken(
      { userId: decoded.userId, sessionId: session._id },
      "7d",
    );
    const newRefreshTokenHash = await bcrypt.hash(newRefreshToken, 10);
    session.refreshTokenHash = newRefreshTokenHash;
    await session.save();

    res.cookie("refreshToken", newRefreshToken, {
      httpOnly: true,
      secure: process.env.NODE_ENV === "production",
      sameSite: "strict",
      maxAge: 7 * 24 * 60 * 60 * 1000,
    });

    return res.status(200).json({
      success: true,
      accessToken,
    });
  } catch (error) {
    console.error(error);
    return res.status(401).json({
      success: false,
      message: "Invalid refresh token",
    });
  }
}

export async function logout(req, res) {
  try {
    const { refreshToken } = req.cookies;

    if (!refreshToken) {
      return res.status(401).json({
        success: false,
        message: "Refresh token not found",
      });
    }

    const decoded = jwt.verify(refreshToken, config.JWT_SECRET);

    const session = await Session.findOne({
      _id: decoded.sessionId,
      user: decoded.userId,
      revoked: false,
    });

    if (!session) {
      return res.status(401).json({
        success: false,
        message: "Invalid refresh token",
      });
    }

    const isValid = await bcrypt.compare(
      refreshToken,
      session.refreshTokenHash,
    );

    if (!isValid) {
      return res.status(401).json({
        success: false,
        message: "Invalid refresh token",
      });
    }

    session.revoked = true;
    await session.save();

    res.clearCookie("refreshToken");

    return res.status(200).json({
      success: true,
      message: "Logout successfully",
    });
  } catch (error) {
    console.error(error);
    return res.status(500).json({
      success: false,
      message: "Internal Server Error",
    });
  }
}

export async function logoutAll(req, res) {
  try {
    const refreshToken = req.cookies.refreshToken;
    if (!refreshToken) {
      return res.status(401).json({
        success: false,
        message: "Unauthorized",
      });
    }

    const decoded = jwt.verify(refreshToken, config.JWT_SECRET);

    await Session.updateMany(
      { user: decoded.userId, revoked: false },
      { revoked: true },
    );

    res.clearCookie("refreshToken");
    return res.status(200).json({
      success: true,
      message: "Logged out from all devices successfully",
    });
  } catch (error) {
    console.error(error);
    return res.status(401).json({
      success: false,
      message: "Invalid refresh token",
    });
  }
}
