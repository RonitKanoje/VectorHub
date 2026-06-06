import { useEffect } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import toast from "react-hot-toast";

const OAuthCallback = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();

  useEffect(() => {
    const status = searchParams.get("status");
    const accessToken = searchParams.get("accessToken");
    const message = searchParams.get("message");

    if (status === "success" && accessToken) {
      localStorage.setItem("accessToken", accessToken);
      toast.success(message || "Login successful");
      navigate("/chat");
      return;
    }

    if (status === "register") {
      toast.error(message || "Please register first");
      navigate("/register");
      return;
    }

    navigate("/");
  }, [navigate, searchParams]);

  return null;
};

export default OAuthCallback;
