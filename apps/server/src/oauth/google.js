import { Google } from "arctic";
import {
  GOOGLE_CWT_CLIENT_SECRET,
  GOOGLE_CWT_CLIENT_ID,
} from "../config/config";

export const google = new Google(
  GOOGLE_CWT_CLIENT_SECRET,
  GOOGLE_CWT_CLIENT_ID,
  "http://localhost:3000/callback",
);
