import { useNavigate } from "react-router-dom";
import HeroHeader from "../components/HeroHeader";
import LoginForm from "../components/LoginForm";

const Home = () => {
  const navigate = useNavigate();

  const handleRegisterClick = () => {
    navigate("/register");
  };

  return (
    <div className="min-h-screen bg-black flex flex-col justify-center items-center px-4 relative overflow-hidden">
      <HeroHeader />
      <LoginForm onRegisterClick={handleRegisterClick} />
    </div>
  );
};

export default Home;