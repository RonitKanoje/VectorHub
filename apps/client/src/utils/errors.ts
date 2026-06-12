interface ApiErrorDetail {
  loc?: Array<string | number>;
  msg?: string;
}

interface ApiErrorData {
  message?: string;
  detail?: string | ApiErrorDetail[];
}

interface ApiErrorLike {
  response?: {
    data?: ApiErrorData;
  };
}

export function getApiErrorMessage(error: unknown, fallback: string) {
  const data = (error as ApiErrorLike).response?.data;

  if (typeof data?.message === "string" && data.message.trim()) {
    return data.message;
  }

  if (typeof data?.detail === "string" && data.detail.trim()) {
    return data.detail;
  }

  if (Array.isArray(data?.detail) && data.detail.length > 0) {
    return data.detail
      .map((item) => {
        const location = item.loc?.join(".") || "request";
        return item.msg ? `${location}: ${item.msg}` : location;
      })
      .join("; ");
  }

  if (error instanceof Error && error.message.trim()) {
    return error.message;
  }

  return fallback;
}
