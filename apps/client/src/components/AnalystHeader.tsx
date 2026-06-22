import { BarChart2, Moon, Sun } from "lucide-react";

interface AnalystHeaderProps {
  mode: string;
  onToggleTheme: () => void;
}

const AnalystHeader = ({ mode, onToggleTheme }: AnalystHeaderProps) => {
  return (
    <div className="flex h-16 shrink-0 items-center justify-between border-b border-slate-800 bg-slate-900/90 px-6 backdrop-blur">
      <div className="flex items-center gap-3">
        <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-violet-600 text-white">
          <BarChart2 className="h-4 w-4" />
        </div>
        <div>
          <h2 className="text-sm font-semibold text-white">Analyst Mode</h2>
          <p className="text-xs text-slate-400">Multi-agent data analysis</p>
        </div>
      </div>
      <button
        onClick={onToggleTheme}
        className="p-2 rounded-full text-slate-400 hover:text-white hover:bg-slate-800 transition"
      >
        {mode === "light" ? <Moon className="h-5 w-5" /> : <Sun className="h-5 w-5" />}
      </button>
    </div>
  );
};

export default AnalystHeader;