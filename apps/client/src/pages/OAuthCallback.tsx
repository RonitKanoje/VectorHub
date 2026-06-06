import { useEffect, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import toast from "react-hot-toast";
import api from "../services/api";

const OAuthCallback = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const handleCallback = async () => {
      try {
        const status = searchParams.get("status");
        const accessToken = searchParams.get("accessToken");
        const message = searchParams.get("message");

        if (status === "success" && accessToken) {
          toast.success(message || "Login successful");
          localStorage.setItem("accessToken", accessToken);
          navigate("/chat");
          return;
        }

        if (status === "register") {
          toast.error(message || "Please register before using Google sign in");
          navigate("/register");
          return;
        }

        // The OAuth callback is handled by the backend
        const code = searchParams.get("code");
        const state = searchParams.get("state");

        if (!code || !state) {
          throw new Error("Missing OAuth parameters");
        }

        // The backend handles the full OAuth flow and returns the response
        const response = await api.get(
          `/api/auth/google/callback?code=${code}&state=${state}`,
        );

        if (response.data.success) {
          // User logged in successfully
          toast.success(response.data.message);
          localStorage.setItem("accessToken", response.data.accessToken);
          navigate("/chat");
        } else if (response.data.redirect) {
          // User doesn't exist, redirect to manual registration.
          navigate("/register");
        }
      } catch (error: any) {
        console.error(error);
        toast.error(error.response?.data?.message || "OAuth login failed");
        navigate("/");
      } finally {
        setLoading(false);
      }
    };

    handleCallback();
  }, [navigate, searchParams]);

  if (loading) {
    return (
      <div className="min-h-screen bg-black flex flex-col justify-center items-center">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-[#00f0ff]"></div>
        <p className="text-zinc-400 mt-4">Processing login...</p>
      </div>
    );
  }

  return null;
};

export default OAuthCallback;
