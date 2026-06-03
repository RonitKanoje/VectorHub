import { useState } from "react";
import { RiAddLargeLine } from "@remixicon/react";
import Options from "./Options";

const PlusButton = () => {
  const [showOptions, setShowOptions] = useState(false);

  return (
    <div className="relative ">
      <button
        className="absolute left-3 top-1/2 -translate-y-1/2"
        onClick={() => setShowOptions((prev) => !prev)}
      >
        <RiAddLargeLine size={18} color="black" />
      </button>

      {showOptions && (
        <div className="absolute left-0 top-full mt-2 bg-white border border-zinc-200 rounded-xl shadow-xl p-2 z-10">
          <Options />
        </div>
      )}
    </div>
  );
};

export default PlusButton;
