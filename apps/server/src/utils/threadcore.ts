import { Request, Response } from "express";
import config from "../config/config.js";
import jwt from "jsonwebtoken";

interface ThreadCoreOptions {
  method?: string;
  body?: unknown;
}

interface ThreadCoreErrorDetail {
  loc?: Array<string | number>;
  msg?: string;
}

interface ThreadCoreErrorResponse {
  detail?: string | Array<ThreadCoreErrorDetail>;
  message?: string;
}

function generateInternalToken(userId: string): string {
  const secret = process.env.INTERNAL_API_SECRET;

  if (!secret) {
    throw new Error(
      "INTERNAL_API_SECRET is not defined in environment variables",
    );
  }

  return jwt.sign(
    {
      user_id: userId,
      service: "express",
    },
    secret,
    {
      expiresIn: "90s",
    },
  );
}

export async function forwardToThreadCore(
  req: Request,
  res: Response,
  endpoint: string,
  options: ThreadCoreOptions = {},
) {
  try {
    const internalToken = generateInternalToken(req.userId!);

    const method = options.method || "GET";

    const response = await fetch(`${config.THREADCORE_URL}${endpoint}`, {
      method,
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${internalToken}`,
      },
      body: options.body ? JSON.stringify(options.body) : undefined,
    });

    const text = await response.text();
    const data = text ? parseResponseText(text) : {};

    if (!response.ok && !data.message) {
      data.message = formatThreadCoreError(data);
    }

    if (!response.ok) {
      console.error(`ThreadCore ${method} ${endpoint} failed`, data);
    }

    return res.status(response.status).json(data);
  } catch (error) {
    console.error("ThreadCore proxy failed", {
      endpoint,
      url: `${config.THREADCORE_URL}${endpoint}`,
      error,
      cause: error instanceof Error ? error.cause : undefined,
    });

    return res.status(502).json({
      success: false,
      message: "FastAPI service is unavailable",
    });
  }
}

function parseResponseText(text: string) {
  try {
    return JSON.parse(text);
  } catch {
    return { message: text };
  }
}

function formatThreadCoreError(data: ThreadCoreErrorResponse) {
  if (Array.isArray(data?.detail)) {
    const errors: string[] = [];

    for (const item of data.detail) {
      const location = Array.isArray(item.loc) ? item.loc.join(".") : "request";

      errors.push(`${location}: ${item.msg}`);
    }

    return errors.join("; ");
  }

  if (typeof data?.detail === "string") {
    return data.detail;
  }

  return "AI request failed";
}

export async function forwardStreamToThreadCore(
  req: Request,
  res: Response,
  endpoint: string,
  options: ThreadCoreOptions = {},
) {
  try {
    const internalToken = generateInternalToken(req.userId!);

    const method = options.method || "GET";

    const response = await fetch(`${config.THREADCORE_URL}${endpoint}`, {
      method,
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${internalToken}`,
      },
      body: options.body ? JSON.stringify(options.body) : undefined,
    });

    if (!response.ok) {
      const text = await response.text();
      const data = text ? parseResponseText(text) : {};

      data.message = formatThreadCoreError(data);

      console.error(`ThreadCore streaming ${method} ${endpoint} failed`, data);

      return res.status(response.status).json(data);
    }

    res.setHeader("Content-Type", "text/event-stream");
    res.setHeader("Cache-Control", "no-cache");
    res.setHeader("Connection", "keep-alive");

    if (response.body) {
      for await (const chunk of response.body) {
        res.write(chunk);
      }
    }

    res.end();
  } catch (error) {
    console.error("ThreadCore stream proxy failed:", error);

    if (!res.headersSent) {
      return res.status(502).json({
        success: false,
        message: "FastAPI service is unavailable for streaming",
      });
    }

    res.end();
  }
}
