import Otp from "./pages/Otp";
import Register from "./pages/Register";
import Chat from "./pages/Chat";
import OAuthCallback from "./pages/OAuthCallback";
import Home from "./pages/Home";
import { Routes, Route } from "react-router-dom";
import { Toaster } from "react-hot-toast";
import { useEffect } from "react";
import { useDispatch } from "react-redux";
import ProtectedRoute from "./components/ProtectedRoute";
import { setCredentials, finishLoading } from "./redux/features/authSlice";
import api from "./services/api";

const App = () => {
  const dispatch = useDispatch();

  useEffect(() => {
    const refreshAuth = async () => {
      try {
        const response = await api.post("/api/auth/refresh-token", {});

        dispatch(setCredentials(response.data.accessToken));
      } catch {
        dispatch(finishLoading());
      }
    };

    refreshAuth();
  }, [dispatch]);

  return (
    <div className="min-h-screen bg-[#f6f8fb] text-[#161b22]">
      <Toaster
        position="top-right"
        reverseOrder={false}
        toastOptions={{
          style: {
            background: "#111827",
            color: "#f8fafc",
            border: "1px solid #243244",
          },
        }}
      />

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
