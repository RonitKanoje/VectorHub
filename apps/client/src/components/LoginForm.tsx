import { useState } from "react";
import AuthHeader from "./AuthHeader";
import AuthFooter from "./AuthFooter";
import AnimatedCard from "./AnimatedCard";
import api from "../services/api";
import { useNavigate } from "react-router-dom";
import toast from "react-hot-toast";
import { FcGoogle } from "react-icons/fc";
import { useDispatch } from "react-redux";
import type { AppDispatch } from "../redux/store";
import { setCredentials } from "../redux/features/authSlice";
import { getApiErrorMessage } from "../utils/errors";

interface LoginFormProps {
  onRegisterClick: () => void;
}

const LoginForm = ({ onRegisterClick }: LoginFormProps) => {
  const [username, setUsername] = useState<string>("");
  const [password, setPassword] = useState<string>("");

  const dispatch = useDispatch<AppDispatch>();

  const navigate = useNavigate();

  const verify = async () => {
    try {
      const response = await api.post("/api/auth/login", {
        username,
        password,
      });

      toast.success("Login successful");

      dispatch(setCredentials(response.data.accessToken));

      navigate("/chat");
    } catch (error: unknown) {
      toast.error(getApiErrorMessage(error, "Something went wrong"));
    }
  };

  return (
    <AnimatedCard>
      <AuthHeader
        title="Welcome Back"
        subtitle="Enter your credentials to access your console"
      />

      {/* Inputs & Actions */}
      <div className="flex flex-col gap-4">
        <input
          type="text"
          placeholder="Username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          className="w-full h-12 px-4 bg-[#121214] border border-zinc-800 rounded-xl focus:outline-none focus:ring-1 focus:ring-[#00f0ff] focus:border-[#00f0ff] transition-all duration-200 placeholder-zinc-600 text-white text-sm"
        />

        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="w-full h-12 px-4 bg-[#121214] border border-zinc-800 rounded-xl focus:outline-none focus:ring-1 focus:ring-[#00f0ff] focus:border-[#00f0ff] transition-all duration-200 placeholder-zinc-600 text-white text-sm"
        />

        {/* Login Button */}
        <button
          className="w-full h-12 bg-white text-black hover:bg-zinc-200 font-bold rounded-xl transition-all duration-200 active:scale-[0.95] cursor-pointer text-sm"
          onClick={() => {
            verify();
          }}
        >
          Login
        </button>

        {/* Divider */}
        <div className="flex items-center gap-3 my-2">
          <div className="flex-1 h-px bg-zinc-700"></div>
          <span className="text-zinc-500 text-xs">OR</span>
          <div className="flex-1 h-px bg-zinc-700"></div>
        </div>

        {/* Continue with Google Button */}
        <button
          className="w-full h-12 bg-white text-black hover:bg-zinc-200 font-bold rounded-xl transition-all duration-200 active:scale-[0.95] cursor-pointer text-sm flex items-center justify-center gap-2"
          onClick={() => {
            window.location.href = "http://localhost:3000/api/auth/google";
          }}
        >
          <FcGoogle size={22} />
          Continue with Google
        </button>
      </div>

      <AuthFooter
        question="Don't have an account?"
        linkText="Register now"
        onLinkClick={onRegisterClick}
      />
    </AnimatedCard>
  );
};

export default LoginForm;
