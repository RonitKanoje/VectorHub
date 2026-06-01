import nodemailer from "nodemailer";
import config from "../config/config.js";

/// all steps are mention in this github repo github.com/ankurdotio/Difference-Backend-video/tree/main/026-nodemailer

const transporter = nodemailer.createTransport({
  // transporter smtp server=> server those handle email
  service: "gmail",

  auth: {
    type: "OAuth2",
    user: config.GOOGLE_USER,
    clientId: config.GOOGLE_CLIENT_ID,
    clientSecret: config.GOOGLE_CLIENT_SECRET,
    refreshToken: config.GOOGLE_REFRESH_TOKEN,
  },
});

// verify the crendential for better practice
transporter.verify((error, success) => {
  if (error) {
    console.error("Error connecting to mail server:", error);
  } else {
    console.log("mail is ready to send message");
  }
});

export const sendEmail = async (to, subject, text, html) => {
  try {
    const info = await transporter.sendMail({
      from: `"Your Name" <${config.GOOGLE_USER}>`,
      to,
      subject,
      text,
      html,
    });

    console.log("Message sent ", info.messageId);
    console.log("Preview URL ", nodemailer.getTestMessageUrl(info));
  } catch (error) {
    console.log("Getting this error on sending the email", error);
  }
};
