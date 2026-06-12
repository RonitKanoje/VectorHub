import type { ReactNode } from "react";

interface OptionsButtonProps {
  icon: ReactNode;
  text: string;
  onClick: () => void;
}

const OptionsButton = ({ icon, text, onClick }: OptionsButtonProps) => {
  return (
    <button
      type="button"
      className="flex w-full items-center gap-3 rounded-xl px-3 py-3 text-left text-sm text-slate-700 transition hover:bg-cyan-50 hover:text-slate-950 active:scale-[0.98]"
      onClick={onClick}
    >
      <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-slate-100 text-cyan-700">
        {icon}
      </span>
      {text}
    </button>
  );
};

export default OptionsButton;
