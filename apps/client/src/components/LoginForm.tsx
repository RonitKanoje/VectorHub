import { useState } from "react";
import AuthHeader from "./AuthHeader";
import AuthFooter from "./AuthFooter";
import AnimatedCard from "./AnimatedCard";
import axios from "axios";
import { useNavigate } from "react-router-dom";
import toast from "react-hot-toast";

interface LoginFormProps {
  onRegisterClick: () => void;
}

const LoginForm = ({ onRegisterClick }: LoginFormProps) => {
  const [username, setUsername] = useState<string>("");
  const [password, setPassword] = useState<string>("");

  const navigate = useNavigate();

  const verify = async () => {
    try {
      const response = await axios.post(
        "http://localhost:3000/api/auth/login",
        {
          username,
          password,
        },
      );

      toast.success("Login successful");
      navigate("/login/otp");
    } catch (error: any) {
      toast.error(error.response?.data?.message || "Something went wrong");
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
