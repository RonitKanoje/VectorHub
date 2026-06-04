import { useState, useEffect } from "react";
import AuthHeader from "./AuthHeader";
import AuthFooter from "./AuthFooter";
import AnimatedCard from "./AnimatedCard";
import axios from "axios";
import { useNavigate, useLocation } from "react-router-dom";
import toast from "react-hot-toast";

interface RegisterFormProps {
  onLoginClick: () => void;
}

const RegisterForm = ({ onLoginClick }: RegisterFormProps) => {
  const [name, setName] = useState("");
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [isGoogleOAuth, setIsGoogleOAuth] = useState(false);
  const [googleUserId, setGoogleUserId] = useState<string | null>(null);

  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    // Check if we have OAuth pre-filled data
    const state = (location.state as any) || null;
    if (state?.email && state?.name) {
      setEmail(state.email);
      setName(state.name);
      setIsGoogleOAuth(true);
      if (state.googleUserId) {
        setGoogleUserId(state.googleUserId);
      }
    }
  }, [location]);

  const register = async () => {
    try {
      // Validation
      if (!name || !username || !email) {
        toast.error("Please fill in all required fields");
        return;
      }

      if (!isGoogleOAuth) {
        if (!password || !confirmPassword) {
          toast.error("Please enter password");
          return;
        }
        if (password !== confirmPassword) {
          toast.error("Passwords do not match");
          return;
        }
      }

      const response = await axios.post(
        "http://localhost:3000/api/auth/register",
        {
          name,
          username,
          email,
          password: isGoogleOAuth ? "google_oauth_" + googleUserId : password,
          confirmPassword: isGoogleOAuth
            ? "google_oauth_" + googleUserId
            : confirmPassword,
          isGoogleOAuth,
          googleUserId,
        },
      );

      if (response.data.success) {
        toast.success("Account created successfully!");
        if (isGoogleOAuth) {
          // Auto-login for Google OAuth users
          navigate("/chat");
        } else {
          navigate("/");
        }
      }
    } catch (error: any) {
      toast.error(error.response?.data?.message || "Registration failed");
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
          disabled={isGoogleOAuth}
          className="w-full h-12 px-4 bg-[#121214] border border-zinc-800 rounded-xl focus:outline-none focus:ring-1 focus:ring-[#00f0ff] focus:border-[#00f0ff] transition-all duration-200 placeholder-zinc-600 text-white text-sm disabled:opacity-50 disabled:cursor-not-allowed"
        />

        {/* Side-by-side passwords */}
        {!isGoogleOAuth && (
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
        )}

        {isGoogleOAuth && (
          <div className="text-center text-sm text-zinc-400">
            Registering with Google - Email verified automatically
          </div>
        )}

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
