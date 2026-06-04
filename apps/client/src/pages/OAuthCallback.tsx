import { useEffect, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import axios from "axios";
import toast from "react-hot-toast";

const OAuthCallback = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const handleCallback = async () => {
      try {
        // The OAuth callback is handled by the backend
        // The backend will redirect here if user needs to register
        const code = searchParams.get("code");
        const state = searchParams.get("state");

        if (!code || !state) {
          throw new Error("Missing OAuth parameters");
        }

        // The backend handles the full OAuth flow
        // Check if we have registration data in the response
        const response = await axios.get(
          `http://localhost:3000/api/auth/google/callback?code=${code}&state=${state}`,
          {
            withCredentials: true,
          },
        );

        if (response.data.success) {
          // User logged in successfully
          toast.success(response.data.message);
          localStorage.setItem("accessToken", response.data.accessToken);
          navigate("/chat");
        } else if (response.data.redirect) {
          // User doesn't exist, redirect to registration with pre-filled data
          navigate("/register", {
            state: {
              email: response.data.userData.email,
              name: response.data.userData.name,
              googleUserId: response.data.userData.googleUserId,
            },
          });
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
