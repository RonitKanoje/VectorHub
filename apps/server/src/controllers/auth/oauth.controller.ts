import { Request, Response } from "express";
import User from "../../models/user.model.js";
import Account from "../../models/account.model.js";
import Session from "../../models/session.model.js";
import crypto from "crypto";
import jwt from "jsonwebtoken";
import bcrypt from "bcrypt";
import { google } from "../../oauth/google.js";
import config from "../../config/config.js";
import { OAUTH_EXCHANGE_EXPIRY } from "../../config/constants.js";
import { generateToken } from "../../utils/token.utils.js";
import type { IUser } from "../../models/user.model.js";

type UserDocument = IUser & { _id: string }; // add _id property to IUser type

function generateCodeVerifier() {
  return crypto.randomBytes(32).toString("base64url");
}

function shouldReturnJson(req: Request) {
  const accept = req.get("Accept") || "";
  return (
    req.xhr ||
    (accept.includes("application/json") && !accept.includes("text/html"))
  );
}

function buildClientRedirect(
  path: string,
  params: Record<string, string | undefined>, 
) {
  const url = new URL(path, config.CLIENT_URL);
  for (const [key, value] of Object.entries(params)) {
    if (value !== undefined && value !== null) {
      url.searchParams.set(key, value);
    }
  }
  return url.toString();
}

export const googleLoginPage = async (req: Request, res: Response) => {
  try {
    const state = crypto.randomUUID();
    const codeVerifier = generateCodeVerifier();

    const url = google.createAuthorizationURL(state, codeVerifier, [
      "email",
      "profile",
    ]);

    const cookieConfig = {
      httpOnly: true,
      secure: config.NODE_ENV === "production",
      maxAge: OAUTH_EXCHANGE_EXPIRY,
      sameSite: "lax",
    } as const;

    res.cookie("google_oauth_state", state, cookieConfig);
    res.cookie("google_code_verifier", codeVerifier, cookieConfig);

    res.redirect(url.toString());
  } catch (error) {
    console.error(error);
    return res.status(500).json({
      success: false,
      message: "Failed to initiate Google login",
    });
  }
};

export const getGoogleLoginCallBack = async (req: Request, res: Response) => {
  try {
    const { code, state } = req.query;

    const { google_oauth_state, google_code_verifier } = req.cookies;

    if (
      !code ||
      !state ||
      !google_oauth_state ||
      !google_code_verifier ||
      state !== google_oauth_state
    ) {
      return res.status(400).json({
        success: false,
        message: "Invalid Login Attempt",
      });
    }

    let tokens;
    try {
      tokens = await google.validateAuthorizationCode(
        code as string,
        google_code_verifier as string,
      );
    } catch (error) {
      console.error(error);
      return res.status(400).json({
        success: false,
        message: "Invalid Login Attempt",
      });
    }

    const idToken = tokens.idToken();
    const claims = jwt.decode(idToken) as {
      sub?: string;
      name?: string;
      email?: string;
    } | null;
    const { sub: googleUserId, name, email } = claims || {};

    if (!email) {
      return res.status(400).json({
        success: false,
        message: "Unable to retrieve email from Google",
      });
    }

    const account = await Account.findOne({
      provider: "google",
      providerAccountId: googleUserId,
    }).populate<{ userId: UserDocument }>("userId");

    if (account?.userId) {
      const user = account.userId;

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

      const refreshTokenHash = await bcrypt.hash(refreshToken, 10);
      session.refreshTokenHash = refreshTokenHash;
      await session.save();

      res.cookie("refreshToken", refreshToken, {
        httpOnly: true,
        sameSite: "strict",
        maxAge: 7 * 24 * 60 * 60 * 1000,
      });

      res.clearCookie("google_oauth_state");
      res.clearCookie("google_code_verifier");

      const payload = {
        success: true,
        message: "Login successful",
        accessToken,
        user: {
          id: user._id,
          name: user.name,
          email: user.email,
          username: user.username,
        },
      };

      if (!shouldReturnJson(req)) {
        return res.redirect(
          buildClientRedirect("/oauth/callback", {
            status: "success",
            message: payload.message,
            accessToken,
          }),
        );
      }

      return res.status(200).json(payload);
    }

    let user = await User.findOne({ email });

    if (user) {
      await Account.findOneAndUpdate(
        {
          provider: "google",
          providerAccountId: googleUserId,
        },
        {
          $setOnInsert: {
            userId: user._id,
            provider: "google",
            providerAccountId: googleUserId,
          },
        },
        {
          upsert: true,
          new: true,
          setDefaultsOnInsert: true,
        },
      );

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
      const refreshTokenHash = await bcrypt.hash(refreshToken, 10);
      session.refreshTokenHash = refreshTokenHash;
      await session.save();

      res.cookie("refreshToken", refreshToken, {
        httpOnly: true,
        sameSite: "strict",
        maxAge: 7 * 24 * 60 * 60 * 1000,
      });

      res.clearCookie("google_oauth_state");
      res.clearCookie("google_code_verifier");

      const payload = {
        success: true,
        message: "Google OAuth linked and login successful",
        accessToken,
        user: {
          id: user._id,
          name: user.name,
          email: user.email,
          username: user.username,
        },
      };

      if (!shouldReturnJson(req)) {
        return res.redirect(
          buildClientRedirect("/oauth/callback", {
            status: "success",
            message: payload.message,
            accessToken,
          }),
        );
      }

      return res.status(200).json(payload);
    }

    res.clearCookie("google_oauth_state");
    res.clearCookie("google_code_verifier");

    const payload = {
      success: false,
      message: "Please register before using Google sign in.",
      redirect: true,
    };

    if (!shouldReturnJson(req)) {
      return res.redirect(
        buildClientRedirect("/oauth/callback", {
          status: "register",
          message: payload.message,
        }),
      );
    }

    return res.status(200).json(payload);
  } catch (error) {
    console.error(error);
    return res.status(500).json({
      success: false,
      message: "Internal Server Error",
    });
  }
};
