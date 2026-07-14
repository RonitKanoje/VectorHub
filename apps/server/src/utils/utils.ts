export const generateOtp = (): string => {
  return Math.floor(100000 + Math.random() * 900000).toString();
};

// we will send otp in html format
export function getOtpHtml(otp: string): string {
  return `
    <html>
      <body style="font-family: Arial, sans-serif; padding: 20px;">

        <h2>OTP Verification</h2>

        <p>Your OTP for verification is:</p>  

        <h1 style="color: blue; letter-spacing: 5px;">
          ${otp}
        </h1>

        <p>This OTP is valid for 10 minutes.</p>

      </body>
    </html>
  `;
}
