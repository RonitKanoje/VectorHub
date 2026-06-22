import { FileSpreadsheet } from "lucide-react";
import type { AnalystChatMessage as AnalystChatMessageType } from "../types/analyst";

interface AnalystSystemMessageProps {
  message: AnalystChatMessageType;
}

const AnalystSystemMessage = ({ message }: AnalystSystemMessageProps) => {
  return (
    <div className="flex justify-center">
      <div className="flex items-center gap-2 rounded-xl border border-violet-800/50 bg-violet-900/20 px-3 py-1.5 text-xs text-violet-300">
        <FileSpreadsheet className="h-3.5 w-3.5 shrink-0" />
        <span>{message.mediaAttachment?.name ?? message.content}</span>
        <span className="text-violet-500">— uploaded ✓</span>
      </div>
    </div>
  );
};

export default AnalystSystemMessage;