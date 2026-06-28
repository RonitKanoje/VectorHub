import { CircleCheck, Clock3, Moon, Sun } from "lucide-react";
import { useDispatch, useSelector } from "react-redux";
import { toggleTheme } from "../redux/features/themeSlice";
import type { RootState, AppDispatch } from "../redux/store";

interface ChatHeaderProps {
  title: string;
  status?: string | null;
}

const ChatHeader = ({ title, status }: ChatHeaderProps) => {
  const isReady = status === "completed";
  const dispatch = useDispatch<AppDispatch>();
  const mode = useSelector((state: RootState) => state.theme.mode);

  return (
    <div className="flex h-16 items-center justify-between bg-white dark:bg-slate-950 px-6 shrink-0">
      <div className="flex items-center gap-3">
        <div>
          <h2 className="text-sm font-semibold text-slate-950 dark:text-white">
            {title}
          </h2>
        </div>
      </div>

      <div className="flex items-center gap-3">
        {status && (
          <div className="flex items-center gap-2 rounded-full border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 px-3 py-1.5 text-xs font-medium text-slate-600 dark:text-slate-300">
            {isReady ? (
              <CircleCheck className="h-3.5 w-3.5 text-cyan-600 dark:text-cyan-400" />
            ) : (
              <Clock3 className="h-3.5 w-3.5 text-amber-600 dark:text-amber-400" />
            )}
            {status}
          </div>
        )}

        <button
          onClick={() => dispatch(toggleTheme())}
          className="p-2 text-slate-500 hover:text-slate-900 dark:text-slate-400 dark:hover:text-white transition-colors rounded-full hover:bg-slate-100 dark:hover:bg-slate-800"
          aria-label="Toggle theme"
        >
          {mode === "light" ? (
            <Moon className="h-5 w-5" />
          ) : (
            <Sun className="h-5 w-5" />
          )}
        </button>
      </div>
    </div>
  );
};

export default ChatHeader;
