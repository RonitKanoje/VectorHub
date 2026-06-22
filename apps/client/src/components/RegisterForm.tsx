import { useState } from "react";
import AuthHeader from "./AuthHeader";
import AuthFooter from "./AuthFooter";
import AnimatedCard from "./AnimatedCard";
import api from "../services/api";
import { useNavigate } from "react-router-dom";
import toast from "react-hot-toast";
import { getApiErrorMessage } from "../utils/errors";

interface RegisterFormProps {
  onLoginClick: () => void;
}

const RegisterForm = ({ onLoginClick }: RegisterFormProps) => {
  const [name, setName] = useState("");
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");

  const navigate = useNavigate();

  const register = async () => {
    try {
      // Validation
      if (!name || !username || !email) {
        toast.error("Please fill in all required fields");
        return;
      }

      if (!password || !confirmPassword) {
        toast.error("Please enter password");
        return;
      }
      if (password !== confirmPassword) {
        toast.error("Passwords do not match");
        return;
      }

      if (username.includes(" ")) {
        toast.error("Username cannot contain spaces");
        return;
      }

      if (password.includes(" ")) {
        toast.error("Password cannot contain spaces");
        return;
      }

      const passwordRegex =
        /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/;
      if (!passwordRegex.test(password)) {
        toast.error(
          "Password must contain at least 8 characters, one uppercase letter, one lowercase letter, one number and one special character"
        );
        return;
      }

      const response = await api.post("/api/auth/register", {
        name,
        username,
        email,
        password,
        confirmPassword,
      });

      if (response.data.success) {
        toast.success("Account created successfully!");
        navigate("/register/otp");
      }
    } catch (error: unknown) {
      toast.error(getApiErrorMessage(error, "Registration failed"));
      console.error(error);
    }
  };

  return (
    <AnimatedCard>
      <AuthHeader
        title="Create Account"
        subtitle="Get started with your developer workspace"
      />

      {/* Inputs & Actions */}
      <div className="flex flex-col gap-4">
        <input
          type="text"
          placeholder="Enter your name"
          value={name}
          onChange={(e) => setName(e.target.value)}
          className="w-full h-12 px-4 bg-[#121214] border border-zinc-800 rounded-xl focus:outline-none focus:ring-1 focus:ring-[#00f0ff] focus:border-[#00f0ff] transition-all duration-200 placeholder-zinc-600 text-white text-sm"
        />

        <input
          type="text"
          placeholder="Username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          className="w-full h-12 px-4 bg-[#121214] border border-zinc-800 rounded-xl focus:outline-none focus:ring-1 focus:ring-[#00f0ff] focus:border-[#00f0ff] transition-all duration-200 placeholder-zinc-600 text-white text-sm"
        />

        <input
          type="email"
          placeholder="Email Address"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="w-full h-12 px-4 bg-[#121214] border border-zinc-800 rounded-xl focus:outline-none focus:ring-1 focus:ring-[#00f0ff] focus:border-[#00f0ff] transition-all duration-200 placeholder-zinc-600 text-white text-sm"
        />

        {/* Side-by-side passwords */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full h-12 px-4 bg-[#121214] border border-zinc-800 rounded-xl focus:outline-none focus:ring-1 focus:ring-[#00f0ff] focus:border-[#00f0ff] transition-all duration-200 placeholder-zinc-600 text-white text-sm"
          />
          <input
            type="password"
            placeholder="Confirm Password"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            className="w-full h-12 px-4 bg-[#121214] border border-zinc-800 rounded-xl focus:outline-none focus:ring-1 focus:ring-[#00f0ff] focus:border-[#00f0ff] transition-all duration-200 placeholder-zinc-600 text-white text-sm"
          />
        </div>

        {/* Create Account Button */}
        <button
          className="w-full h-12 bg-white text-black hover:bg-zinc-200 font-bold rounded-xl transition-all duration-200 active:scale-[0.97] cursor-pointer text-sm mt-2"
          onClick={() => {
            register();
          }}
        >
          Create Account
        </button>
      </div>

      <AuthFooter
        question="Already have an account?"
        linkText="Sign in"
        onLinkClick={onLoginClick}
      />
    </AnimatedCard>
  );
};

export default RegisterForm;
