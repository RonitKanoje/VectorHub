// import Home from "./pages/Home";
import Otp from "./pages/Otp";
import Register from "./pages/Register";
import Chat from "./pages/Chat";
import OAuthCallback from "./pages/OAuthCallback";
import { Routes, Route } from "react-router-dom";
import Home from "./pages/Home";
import { Toaster } from "react-hot-toast";

const App = () => {
  return (
    <div>
      <Toaster position="top-right" reverseOrder={false} />
      <Routes>
        <Route path="/" element={<Home />}></Route>
        <Route path="/register" element={<Register />}></Route>
        <Route path="/register/otp" element={<Otp />}></Route>
        <Route path="/chat" element={<Chat />}></Route>
        <Route path="/oauth/callback" element={<OAuthCallback />}></Route>
      </Routes>
    </div>
  );
};

export default App;
