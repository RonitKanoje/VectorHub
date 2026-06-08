import Otp from "./pages/Otp";
import Register from "./pages/Register";
import Chat from "./pages/Chat";
import OAuthCallback from "./pages/OAuthCallback";
import Home from "./pages/Home";
import { Routes, Route } from "react-router-dom";
import { Toaster } from "react-hot-toast";
import { useEffect } from "react";
import axios from "axios";
import { useDispatch } from "react-redux";
import ProtectedRoute from "./components/ProtectedRoute";
import { setCredentials, finishLoading } from "./redux/features/authSlice";

const App = () => {
  const dispatch = useDispatch();

  useEffect(() => {
    const refreshAuth = async () => {
      try {
        const response = await axios.post(
          "http://localhost:3000/api/auth/refresh-token",
          {},
          {
            withCredentials: true,
          },
        );

        dispatch(setCredentials(response.data.accessToken));
      } catch (error) {
        dispatch(finishLoading());
      }
    };

    refreshAuth();
  }, [dispatch]);

  return (
    <div>
      <Toaster position="top-right" reverseOrder={false} />

      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/register" element={<Register />} />
        <Route path="/register/otp" element={<Otp />} />

        <Route
          path="/chat"
          element={
            <ProtectedRoute>
              <Chat />
            </ProtectedRoute>
          }
        />

        <Route path="/oauth/callback" element={<OAuthCallback />} />
      </Routes>
    </div>
  );
};

export default App;
