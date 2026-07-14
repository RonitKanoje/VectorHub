declare global {
  namespace NodeJS {
    interface ProcessEnv {
      MONGODB_COMPASS_URL?: string;
      JWT_SECRET?: string;
      GOOGLE_USER?: string;
      GOOGLE_CLIENT_ID?: string;
      GOOGLE_CLIENT_SECRET?: string;
      GOOGLE_REFRESH_TOKEN?: string;
      GOOGLE_CONTINUE_WITH_GOOGLE_CLIENT_SECRET?: string;
      GOOGLE_CONTINUE_WITH_GOOGLE_CLIENT_ID?: string;
      CLIENT_URL?: string;
      THREADCORE_URL?: string;
      NODE_ENV?: string;
      PORT?: string;
      GROQ_API_KEY?: string;
    }
  }
}

export {};
