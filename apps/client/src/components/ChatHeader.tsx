import { CircleCheck, Clock3 } from "lucide-react";

interface ChatHeaderProps {
  title: string;
  status?: string | null;
}

const ChatHeader = ({ title, status }: ChatHeaderProps) => {
  const isReady = status === "completed";

  return (
    <div className="flex h-16 items-center justify-between border-b border-slate-200 bg-white/90 px-6 backdrop-blur">
      <div>
        <h2 className="text-sm font-semibold text-slate-950">{title}</h2>
        <p className="text-xs text-slate-500">ThreadCore assistant</p>
      </div>

      {status && (
        <div className="flex items-center gap-2 rounded-full border border-slate-200 bg-slate-50 px-3 py-1.5 text-xs font-medium text-slate-600">
          {isReady ? (
            <CircleCheck className="h-3.5 w-3.5 text-emerald-600" />
          ) : (
            <Clock3 className="h-3.5 w-3.5 text-amber-600" />
          )}
          {status}
        </div>
      )}
    </div>
  );
};

export default ChatHeader;
