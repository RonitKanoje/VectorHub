import { useEffect } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import toast from "react-hot-toast";
import { useDispatch } from "react-redux";
import { setCredentials } from "../redux/features/authSlice";

const OAuthCallback = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const dispatch = useDispatch();

  useEffect(() => {
    const status = searchParams.get("status");
    const accessToken = searchParams.get("accessToken");
    const message = searchParams.get("message");

    if (status === "success" && accessToken) {
      // localStorage.setItem("accessToken", accessToken);
      dispatch(setCredentials(accessToken));
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
  }, [navigate, searchParams, dispatch]);

  return null;
};

export default OAuthCallback;
