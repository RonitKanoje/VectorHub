import { RiArrowUpLine } from "@remixicon/react";
import PlusButton from "./PlusButton";

const MessageInput = ({ messages, setMessages }) => {
  return (
    <div className="relative p-4  bg-white">
      <div className="w-full mx-auto relative">
        <input
          type="text"
          placeholder="Type a message..."
          className="w-full bg-zinc-50 border border-zinc-200 rounded-xl py-3 pl-12 pr-12 text-sm text-zinc-900 placeholder:text-zinc-400 focus:outline-none focus:ring-1 focus:ring-zinc-400 focus:border-zinc-400"
          onKeyDown={(e) => {
            if (e.key === "Enter") {
              e.preventDefault();
              setMessages([...messages, { user: e.currentTarget.value }]);
              e.currentTarget.value = "";
            }
          }}
        />
        {/* Plus Button */}
        <PlusButton />
        {/* Send Button */}
        <button className="absolute right-3 top-1/2 -translate-y-1/2 bg-zinc-900 hover:bg-zinc-800 text-white p-2 rounded-lg">
          <RiArrowUpLine className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
};

export default MessageInput;
