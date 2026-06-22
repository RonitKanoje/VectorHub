import jwt from "jsonwebtoken";

export async function generateToken(payload, expiresIn) {
  return jwt.sign(payload, process.env.JWT_SECRET, { expiresIn: expiresIn });
}
