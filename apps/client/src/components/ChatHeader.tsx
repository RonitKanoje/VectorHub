import { BarChart2, CircleCheck, Clock3, Moon, Sun } from "lucide-react";
import { useDispatch, useSelector } from "react-redux";
import { toggleTheme } from "../redux/features/themeSlice";
import type { RootState } from "../redux/store";

interface ChatHeaderProps {
  title: string;
  status?: string | null;
  isAnalystMode?: boolean;
}

const ChatHeader = ({ title, status, isAnalystMode = false }: ChatHeaderProps) => {
  const isReady = status === "completed";
  const dispatch = useDispatch();
  const mode = useSelector((state: RootState) => state.theme.mode);

  return (
    <div className="flex h-16 items-center justify-between border-b border-slate-200 dark:border-slate-800 bg-white/90 dark:bg-slate-900/90 px-6 backdrop-blur shrink-0">
      <div className="flex items-center gap-3">
        {isAnalystMode && (
          <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-violet-100 dark:bg-violet-900/50 text-violet-600 dark:text-violet-400">
            <BarChart2 className="h-4 w-4" />
          </div>
        )}
        <div>
          <h2 className="text-sm font-semibold text-slate-950 dark:text-white">{title}</h2>
          <p className="text-xs text-slate-500 dark:text-slate-400">
            {isAnalystMode ? "Analyst Agent" : "ThreadCore assistant"}
          </p>
        </div>
      </div>

      <div className="flex items-center gap-3">
        {status && (
          <div className="flex items-center gap-2 rounded-full border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 px-3 py-1.5 text-xs font-medium text-slate-600 dark:text-slate-300">
            {isReady ? (
              <CircleCheck className="h-3.5 w-3.5 text-emerald-600 dark:text-emerald-400" />
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
          {mode === "light" ? <Moon className="h-5 w-5" /> : <Sun className="h-5 w-5" />}
        </button>
      </div>
    </div>
  );
};

export default ChatHeader;
