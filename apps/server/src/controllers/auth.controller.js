import User from "../models/user.model.js";
import bcrypt from "bcrypt";
import { sendEmail } from "../services/email.sevice.js";
import { generateOtp, getOtpHtml } from "../utils/utils.js";
import jwt from "jsonwebtoken";

export async function register(req, res) {
  try {
    const { name, username, email, password } = req.body;

    const isAlreadyRegistered = await User.findOne({
      $or: [{ email }, { username }],
    });

    if (isAlreadyRegistered) {
      return res.status(400).json({
        success: false,
        message: "User already exists",
      });
    }

    const hashedPassword = await bcrypt.hash(password, 10);

    const user = await User.create({
      name,
      username,
      email,
      password: hashedPassword,
    });

    return res.status(201).json({
      success: true,
      message: "User registered successfully",
      userId: user._id,
    });

    const otp = generateOtp();
    const otpHtml = getOtpHtml(otp);

    const bytes = await bcrypt.hash(otp, 10);
    await otpModel.create({
      email,
      user: user._id,
      otpHash: bytes,
    });

    await sendEmail(email, "OTP Verification", `Your Code is ${otp}`, otpHtml);

    return res.status(201).json({
      success: true,
      message:
        "User registered successfully. OTP sent to email for verification.",
      userId: user._id,
    });
  } catch (error) {
    console.error(error);

    return res.status(500).json({
      success: false,
      message: "Internal Server Error",
    });
  }
}

export async function verifEmail(req, res) {
  const { email, otp } = req.body;

  if (!email || !otp) {
    return res.status(400).json({
      success: false,
      message: "Email and OTP are required",
    });
  }

  const otpEntry = await otpModel.findOne({ email }).sort({ createdAt: -1 });

  if (!otpEntry) {
    return res.status(400).json({ message: "OTP not found or expired" });
  }
  const otpHash = bcrypt.compare(otp, otpEntry.otpHash);

  if (!otpHash) {
    return res.status(400).json({ message: "Invalid OTP" });
  }

  const user = await User.findOne({ email });

  if (!user) {
    return res.status(400).json({ message: "User not found" });
  }

  user.isVerified = true;
  await user.save();

  await otpModel.deleteMany({ email });

  return res.status(200).json({ message: "Email verified successfully" });
}

export async function generateToken(userId, expiresIn) {
  // Implementation for generating token

  return jwt.sign({ userId }, process.env.JWT_SECRET, { expiresIn: expiresIn });
}

// login
export async function login(req, res) {
  try {
    const { email, password } = req.body;

    const user = await User.findOne({ email });
    if (!user) {
      return res.status(400).json({
        success: false,
        message: "Invalid email or password",
      });
    }
    if (!user.isVerified) {
      return res.status(400).json({
        success: false,
        message: "Email not verified", ///  here we have to handle the case when user is not verified and try to login then we have to send the otp again to the user email for verification and then after verification we have to allow the user to login
      });
    }

    const hashedPassword = await bcrypt.compare(password, user.password);

    if (!hashedPassword) {
      return res.status(400).json({
        success: false,
        message: "Invalid email or password",
      });
    }

    const refreshToken = await generateToken(user._id, "7d");

    const refreshTokenHash = await bcrypt.hash(refreshToken, 10);

    const session = await Session.create({
      user: user._id,
      refreshTokenHash,
      ip: req.ip,
      userAgent: req.get("User-Agent"),
    });

    const accessToken = await generateToken(user._id, "15m");

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

    const refreshTokenHash = await bcrypt.hash(refreshToken, 10);

    const session = await Session.findOne({
      user: decoded.userId,
      refreshTokenHash,
      revoked: false,
    });

    if (!session) {
      return res.status(401).json({
        success: false,
        message: "Invalid refresh token",
      });
    }

    const accessToken = await generateToken(decoded.userId, "15m");

    const newRefreshToken = await generateToken(decoded.userId, "7d");
    const newRefreshTokenHash = await bcrypt.hash(newRefreshToken, 10);
    session.refreshTokenHash = newRefreshTokenHash;
    await session.save();

    res.cookie("refreshToken", newRefreshToken, {
      httpOnly: true,
      sameSite: "strict",
      maxAge: 7 * 24 * 60 * 60 * 1000, // 7 days
    });
  } catch (error) {
    console.error(error);
    return res.status(500).json({
      success: false,
      message: "Internal Server Error",
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

    const refreshTokenHash = await bcrypt.hash(refreshToken, 10);
    const session = await Session.findOne({
      refreshTokenHash,
      revoked: false,
    });

    if (!session) {
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
  const refreshToken = req.cookies.refreshToken;
  if (!refreshToken) {
    return res.status(401).json({
      message: "Unauthorized",
    });
  }

  const decoded = jwt.verify(refreshToken, config.JWT_SECRET);

  await Session.updateMany(
    { user: decoded.id, revoked: false },
    { revoked: true },
  );

  res.clearCookie("refreshToken");
  res.status(200).json({
    message: "Logged out from all devices successfully",
  });
}
