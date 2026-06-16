import Otp from "./pages/Otp";
import Register from "./pages/Register";
import Chat from "./pages/Chat";
import Analyst from "./pages/Analyst";
import OAuthCallback from "./pages/OAuthCallback";
import Home from "./pages/Home";
import { Routes, Route } from "react-router-dom";
import { Toaster } from "react-hot-toast";
import { useEffect } from "react";
import { useDispatch, useSelector } from "react-redux";
import ProtectedRoute from "./components/ProtectedRoute";
import { setCredentials, finishLoading } from "./redux/features/authSlice";
import type { RootState } from "./redux/store";
import api from "./services/api";

const App = () => {
  const dispatch = useDispatch();
  const mode = useSelector((state: RootState) => state.theme.mode);

  useEffect(() => {
    if (mode === "dark") {
      document.documentElement.classList.add("dark");
    } else {
      document.documentElement.classList.remove("dark");
    }
  }, [mode]);

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
    <div className="min-h-screen transition-colors duration-200">
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

        <Route
          path="/analyst"
          element={
            <ProtectedRoute>
              <Analyst />
            </ProtectedRoute>
          }
        />

        <Route path="/oauth/callback" element={<OAuthCallback />} />
      </Routes>
    </div>
  );
};

export default App;
