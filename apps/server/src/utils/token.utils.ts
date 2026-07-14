import jwt, { SignOptions } from "jsonwebtoken";

export function generateToken(
  payload: object,
  expiresIn: SignOptions["expiresIn"],
) {
  return jwt.sign(payload, process.env.JWT_SECRET as string, { expiresIn });
}
