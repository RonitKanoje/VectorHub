import { useState } from "react";
import { useNavigate } from "react-router-dom";
import OTPInput from "../components/OTPInput";

const Otp = () => {
  const [otp, setOtp] = useState(["", "", "", "", "", ""]);
  const navigate = useNavigate();

  const handleSubmit = () => {
    const finalOtp = otp.join("");
    console.log(finalOtp);
    navigate("/chat");
  };

  return (
    <div className="bg-mist-800 text-white h-screen flex justify-center items-center">
      <div className="bg-mist-700 p-8 rounded-xl shadow-lg">
        <h1 className="text-3xl font-bold text-center">OTP Verification</h1>

        <p className="text-center mt-2 text-gray-300">
          Enter the OTP sent to your email
        </p>

        <OTPInput otp={otp} setOtp={setOtp} />

        <button
          onClick={handleSubmit}
          className="
            mt-6
            w-full
            h-12
            bg-blue-600
            rounded-lg
            hover:bg-blue-700
            transition
            active:scale-95
          "
        >
          Verify OTP
        </button>
      </div>
    </div>
  );
};

export default Otp;
