import nodemailer from "nodemailer";
import config from "../config/config.js";

const transporter = nodemailer.createTransport({
  service: "gmail",
  auth: {
    type: "OAuth2",
    user: config.GOOGLE_USER,
    clientId: config.GOOGLE_CLIENT_ID,
    clientSecret: config.GOOGLE_CLIENT_SECRET,
    refreshToken: config.GOOGLE_REFRESH_TOKEN,
  },
});

const verifyMailer = async (): Promise<void> => {
  try {
    await transporter.verify();
    console.log("Mail server is ready");
  } catch (error) {
    const message = error instanceof Error ? error.message : error;
    console.error("Error connecting to mail server:", message);
    // Don't throw here
  }
};

verifyMailer();

export const sendEmail = async (
  to: string,
  subject: string,
  text: string,
  html: string,
): Promise<void> => {
  try {
    const info = await transporter.sendMail({
      from: `"Your Name" <${config.GOOGLE_USER}>`,
      to,
      subject,
      text,
      html,
    });

    console.log("Message sent:", info.messageId);
  } catch (error) {
    console.error("Error sending email:", error);
  }
};
