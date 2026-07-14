declare module "cookie-parser" {
  import { RequestHandler } from "express";
  const cookieParser: (secretOrOptions?: string | object) => RequestHandler;
  export default cookieParser;
}
