import { useSelector } from "react-redux";
import type { RootState } from "../redux/store";

const EmptyState = ({ isAnalystMode = false }: { isAnalystMode?: boolean }) => {
  const accessToken = useSelector((state: RootState) => state.auth.accessToken);
  let userName = null;

  if (accessToken) {
    try {
      const payload = JSON.parse(atob(accessToken.split(".")[1]));
      userName =
        payload.username ||
        payload.name ||
        payload.email?.split("@")[0] ||
        null;
    } catch (e) {
      // Ignore parse errors
    }
  }

  const greeting = userName ? `Hello, ${userName} 👋` : "Hello! 👋";

  return (
    <div className="flex flex-col items-center justify-center space-y-3 text-center">
      <h2 className="text-2xl font-semibold text-slate-800 dark:text-slate-200">
        {greeting}
      </h2>
      <p className="text-slate-600 dark:text-slate-400">
        {isAnalystMode
          ? "Upload your datasets and ask analytical questions."
          : "How can I help you today?"}
      </p>
    </div>
  );
};

export default EmptyState;
