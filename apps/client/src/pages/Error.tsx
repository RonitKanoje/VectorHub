import { useNavigate } from "react-router-dom";
import { FiAlertTriangle } from "react-icons/fi";

const ErrorPage = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-black flex items-center justify-center px-6">
      <div className="max-w-md w-full bg-[#0d0d0d] border border-zinc-800 rounded-2xl p-8 text-center shadow-xl">
        <FiAlertTriangle className="mx-auto text-red-500 text-6xl mb-4" />

        <h1 className="text-4xl font-bold text-white mb-2">
          Something went wrong
        </h1>

        <p className="text-zinc-400 mb-8">
          An unexpected error occurred. Please try again or return to the home
          page.
        </p>

        <div className="flex gap-3">
          <button
            onClick={() => window.location.reload()}
            className="flex-1 h-12 bg-zinc-800 hover:bg-zinc-700 text-white rounded-xl transition-all"
          >
            Retry
          </button>

          <button
            onClick={() => navigate("/")}
            className="flex-1 h-12 bg-white text-black font-semibold rounded-xl hover:bg-zinc-200 transition-all"
          >
            Go Home
          </button>
        </div>
      </div>
    </div>
  );
};

export default ErrorPage;
