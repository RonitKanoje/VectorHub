import { Google } from "arctic";
import config from "../config/config.js";

export const google = new Google(
  config.GOOGLE_CWT_CLIENT_ID,
  config.GOOGLE_CWT_CLIENT_SECRET,
  config.GOOGLE_OAUTH_CALLBACK_URL,
);
