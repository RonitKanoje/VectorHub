import { useState } from "react";
import { useNavigate } from "react-router-dom";
import OTPInput from "../components/OTPInput";
import toast from "react-hot-toast";
import { useDispatch } from "react-redux";
import api from "../services/api";
import { setCredentials } from "../redux/features/authSlice";
import type { AppDispatch } from "../redux/store";
import { getApiErrorMessage } from "../utils/errors";

const Otp = () => {
  const [error, setError] = useState("");
  const [otp, setOtp] = useState(["", "", "", "", "", ""]);
  const navigate = useNavigate();
  const dispatch = useDispatch<AppDispatch>();

  const handleSubmit = async () => {
    const finalOtp = otp.join("");

    try {
      const response = await api.post("/api/auth/verify", { otp: finalOtp });
      dispatch(setCredentials(response.data.accessToken));
      toast.success("Email verified");
      navigate("/chat");
    } catch (error: unknown) {
      const message = getApiErrorMessage(error, "Invalid OTP");

      setError(message);
      toast.error(message);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-950 px-4 text-white">
      <div className="w-full max-w-md rounded-2xl border border-white/10 bg-slate-900 p-8 shadow-2xl shadow-cyan-950/30">
        <h1 className="text-center text-3xl font-bold">OTP Verification</h1>

        <p className="mt-2 text-center text-sm text-slate-400">
          Enter the OTP sent to your email
        </p>

        <OTPInput otp={otp} setOtp={setOtp} />
        {error && (
          <p className="mt-4 rounded-xl border border-red-500/30 bg-red-500/10 px-3 py-2 text-center text-sm text-red-200">
            {error}
          </p>
        )}

        <button
          onClick={handleSubmit}
          className="mt-6 h-12 w-full rounded-xl bg-cyan-400 font-semibold text-slate-950 transition hover:bg-cyan-300 active:scale-95"
        >
          Verify OTP
        </button>
      </div>
    </div>
  );
};

export default Otp;
