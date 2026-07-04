import { useSelector } from "react-redux";
import type { RootState } from "../redux/store";

const EmptyState = ({ isAnalystMode = false }: { isAnalystMode?: boolean }) => {
  const accessToken = useSelector((state: RootState) => state.auth.accessToken);

  let nameOfUSer = "";

  if (accessToken) {
    try {
      const payload = JSON.parse(atob(accessToken.split(".")[1]));

      nameOfUSer =
        payload.name || payload.username || payload.email?.split("@")[0] || "";
    } catch {
      nameOfUSer = "";
    }
  }

  const hour = new Date().getHours();

  const greetingPrefix =
    hour < 12 ? "Good Morning" : hour < 17 ? "Good Afternoon" : "Good Evening";

  return (
    <div className="flex flex-col items-center justify-center space-y-3 text-center">
      <h2 className="text-3xl font-semibold text-slate-800 dark:text-slate-200">
        {nameOfUSer
          ? `${greetingPrefix}, ${nameOfUSer}!`
          : `${greetingPrefix} !!`}
      </h2>

      <p className="max-w-lg text-slate-600 dark:text-slate-400">
        {isAnalystMode
          ? "Upload your dataset and ask analytical questions. I'll help you explore, summarize, and visualize your data."
          : "How can I help you today?"}
      </p>
    </div>
  );
};

export default EmptyState;
