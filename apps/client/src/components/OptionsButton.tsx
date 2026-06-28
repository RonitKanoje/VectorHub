import type { ReactNode } from "react";

interface OptionsButtonProps {
  icon: ReactNode;
  text: string;
  subtitle?: string;
  onClick: () => void;
}

const OptionsButton = ({ icon, text, subtitle, onClick }: OptionsButtonProps) => {
  return (
    <button
      type="button"
      className="flex w-full items-center gap-3 rounded-xl px-3 py-3 text-left text-sm text-slate-700 dark:text-slate-300 transition hover:bg-cyan-50 dark:hover:bg-slate-800 hover:text-slate-950 dark:hover:text-white active:scale-[0.98]"
      onClick={onClick}
    >
      <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-slate-100 dark:bg-slate-950 text-cyan-700 dark:text-cyan-400">
        {icon}
      </span>
      <div className="flex flex-col">
        <span className="font-medium">{text}</span>
        {subtitle && <span className="text-xs text-slate-400 dark:text-slate-500">{subtitle}</span>}
      </div>
    </button>
  );
};

export default OptionsButton;
