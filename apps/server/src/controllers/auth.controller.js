import User from "../models/user.model.js";
import otpModel from "../models/otp.model.js";
import bcrypt from "bcrypt";
import { sendEmail } from "../services/email.sevice.js";
import { generateOtp, getOtpHtml } from "../utils/utils.js";
import jwt from "jsonwebtoken";
import verificationToken from "../models/verificationToken.model.js";
import { generalState, generateCodeVerifier } from "arctic";
import { OAUTH_EXCHANGE_EXPIRY } from "../config/constants.js";

export async function register(req, res) {
  try {
    const { name, username, email, password, confirmPassword } = req.body;

    const requiredFields = {
      name,
      username,
      email,
      password,
      confirmPassword,
    };

    for (const [field, value] of Object.entries(requiredFields)) {
      if (!value || value.trim() === "") {
        return res.status(400).json({
          success: false,
          message: `${field} is required`,
        });
      }
    }

    if (password !== confirmPassword) {
      return res.status(400).json({
        success: false,
        message: "Passwords do not match",
      });
    }

    const paaswordRegex =
      /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/;

    if (!passwordRegex.test(password)) {
      return res.status(400).json({
        success: false,
        message:
          "Password must contain at least 8 characters, one uppercase letter, one lowercase letter, one number and one special character",
      });
    }

    if (username.includes(" ")) {
      return res.status(400).json({
        success: false,
        message: "Username cannot contain spaces",
      });
    }

    if (password.includes(" ")) {
      return res.status(400).json({
        success: false,
        message: "Password cannot contain spaces",
      });
    }

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

    const otp = generateOtp();
    const otpHtml = getOtpHtml(otp);

    const bytes = await bcrypt.hash(otp, 10);
    await otpModel.create({
      email,
      user: user._id,
      otpHash: bytes,
    });

    const verificationToken = crypto.randomUUID();

    await verificationToken.create({
      user: user._id,
      otpHash: bytes,
      verificationToken,
      expiresAt: new Date(Date.now() + 10 * 60 * 1000),
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
    const { verificationToken, otp } = req.body;

    if (!verificationToken || !otp) {
      return res.status(400).json({
        success: false,
        message: "Verification token and OTP are required",
      });
    }

    const verificationRecord = await verificationTokenModel.findOne({
      verificationToken,
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

    user.isVerified = true;
    await user.save();

    await verificationTokenModel.deleteOne({
      _id: verificationRecord._id,
    });

    return res.status(200).json({
      success: true,
      message: "Email verified successfully",
    });
  } catch (error) {
    console.error(error);

    return res.status(500).json({
      success: false,
      message: "Internal Server Error",
    });
  }
}

export async function generateToken(userId, expiresIn) {
  // Implementation for generating token

  return jwt.sign({ userId }, process.env.JWT_SECRET, { expiresIn: expiresIn });
}

// login
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

    if (username.includes(" ")) {
      return res.status(400).json({
        success: false,
        message: "Username cannot contain spaces",
      });
    }

    if (password.includes(" ")) {
      return res.status(400).json({
        success: false,
        message: "Password cannot contain spaces",
      });
    }

    const user = await User.findOne({ username });

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

// get google login page basically we will be fetching all email Id of a particular USer
export const googleLoginPage = async (req, res) => {
  const state = generalState();
  const codeVerifier = generalCodeVerifier();

  // basically we are fetching user email with the help of our client
  const url = google.createAuthorizationURL(state, codeVerifier, [
    "email",
    "profile",
    "email",
  ]);

  const cookieConfig = {
    http: true,
    secure: true,
    maxAge: OAUTH_EXCHANGE_CONFIG,
    sameSite: "lax",
  };

  res.cookie("google_oauth_state", state, cookieConfig);
  res.cookie("google_code_verifier", codeVerifier, cookieConfig);

  res.redirect(url.toString());
};

export const getGoogleLoginCallBack = async (req, res) => {
  const { code, state } = req.query;

  const { google_oauth_state, google_oauth_verifier } = req.cookies;

  
};
