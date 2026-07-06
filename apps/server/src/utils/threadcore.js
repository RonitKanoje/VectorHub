import config from "../config/config.js";

// sending request to FastAPI
export async function forwardToThreadCore(req, res, endpoint, options = {}) {
  try {
    const method = options.method || "GET";
    const response = await fetch(`${config.THREADCORE_URL}${endpoint}`, {
      method,
      headers: {
        "Content-Type": "application/json",
        "X-User-Id": req.userId,
      },
      body: options.body ? JSON.stringify(options.body) : undefined,
    });

    const text = await response.text(); // convert response into text
    const data = text ? parseResponseText(text) : {}; // parse it into json

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
      cause: error.cause,
    });
    return res.status(502).json({
      success: false,
      message: "FastAPI service is unavailable",
    });
  }
}

// parsing json into text
function parseResponseText(text) {
  try {
    return JSON.parse(text);
  } catch {
    return { message: text };
  }
}

// showing FastAPI error in a better way
function formatThreadCoreError(data) {
  if (Array.isArray(data?.detail)) {
    const errors = [];

    for (const item of data.detail) {
      let location;

      if (Array.isArray(item.loc)) {
        location = item.loc.join(".");
      } else {
        location = "request";
      }

      errors.push(`${location}: ${item.msg}`);
    }

    return errors.join("; ");
  } else if (typeof data?.detail === "string") {
    return data.detail;
  } else {
    return "AI request failed";
  }
}

// streaming proxy to FastAPI
export async function forwardStreamToThreadCore(
  req,
  res,
  endpoint,
  options = {},
) {
  try {
    const method = options.method || "GET";
    const response = await fetch(`${config.THREADCORE_URL}${endpoint}`, {
      method,
      headers: {
        "Content-Type": "application/json",
        "X-User-Id": req.userId,
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
