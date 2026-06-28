import User from "../../models/user.model.js";
import otpModel from "../../models/otp.model.js";
import bcrypt from "bcrypt";
import crypto from "crypto";
import { sendEmail } from "../../services/email.sevice.js";
import { generateOtp, getOtpHtml } from "../../utils/utils.js";
import verificationToken from "../../models/verificationToken.model.js";
import Session from "../../models/session.model.js";
import { generateToken } from "../../utils/token.utils.js";

export async function register(req, res) {
  try {
    const { name, username, email, password, confirmPassword } = req.body;

    const requiredFields = { name, username, email };

    for (const [field, value] of Object.entries(requiredFields)) {
      if (!value || value.trim() === "") {
        return res.status(400).json({
          success: false,
          message: `${field} is required`,
        });
      }
    }

    if (!password) {
      return res.status(400).json({
        success: false,
        message: "Password is required",
      });
    }

    // Advanced validations (including confirmPassword mismatch and username spacing)
    // have been moved to the client side.

    const isAlreadyUsername = await User.findOne({ username });
    const isAlreadyEmail = await User.findOne({ email });

    if (isAlreadyUsername) {
      return res.status(400).json({
        success: false,
        message: "Username already exists",
      });
    }

    if (isAlreadyEmail) {
      return res.status(400).json({
        success: false,
        message: "Account with this email already exist try to login",
      });
    }

    const hashedPassword = await bcrypt.hash(password, 10);

    const user = await User.create({
      name,
      username,
      email,
      password: hashedPassword,
    });

    const otp = generateOtp();
    const otpHtml = getOtpHtml(otp);

    const bytes = await bcrypt.hash(otp, 10);
    await otpModel.create({
      email,
      user: user._id,
      otpHash: bytes,
    });

    const verificationTokenValue = crypto.randomUUID();

    await verificationToken.create({
      user: user._id,
      otpHash: bytes,
      verificationToken: verificationTokenValue,
      expiresAt: new Date(Date.now() + 10 * 60 * 1000),
    });

    res.cookie("verificationToken", verificationTokenValue, {
      httpOnly: true,
      secure: process.env.NODE_ENV === "production",
      sameSite: "strict",
      maxAge: 10 * 60 * 1000,
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

export async function verifyEmail(req, res) {
  try {
    const { otp } = req.body;

    if (!otp) {
      return res.status(400).json({
        success: false,
        message: "OTP is required",
      });
    }

    const cookieToken = req.cookies.verificationToken;

    const verificationRecord = await verificationToken.findOne({
      verificationToken: cookieToken,
    });

    if (!verificationRecord) {
      return res.status(400).json({
        success: false,
        message: "Verification token expired or invalid",
      });
    }

    const isOtpValid = await bcrypt.compare(otp, verificationRecord.otpHash);

    if (!isOtpValid) {
      return res.status(400).json({
        success: false,
        message: "Invalid OTP",
      });
    }

    const user = await User.findById(verificationRecord.user);

    if (!user) {
      return res.status(404).json({
        success: false,
        message: "User not found",
      });
    }

    if (verificationRecord.expiresAt < new Date()) {
      await verificationToken.deleteOne({ _id: verificationRecord._id });
      return res.status(400).json({
        success: false,
        message: "Verification token expired",
      });
    }

    user.isVerified = true;
    await user.save();

    const session = await Session.create({
      user: user._id,
      refreshTokenHash: "pending",
      ip: req.ip,
      userAgent: req.get("User-Agent"),
    });

    const refreshToken = await generateToken(
      { userId: user._id, sessionId: session._id },
      "7d",
    );

    const accessToken = await generateToken(
      {
        userId: user._id,
        username: user.username,
        name: user.name,
        email: user.email,
      },
      "15m",
    );

    session.refreshTokenHash = await bcrypt.hash(refreshToken, 10);
    await session.save();

    await verificationToken.deleteOne({ _id: verificationRecord._id });

    res.clearCookie("verificationToken");
    res.cookie("refreshToken", refreshToken, {
      httpOnly: true,
      secure: process.env.NODE_ENV === "production",
      sameSite: "strict",
      maxAge: 7 * 24 * 60 * 60 * 1000,
    });

    return res.status(200).json({
      success: true,
      message: "Email verified successfully",
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
