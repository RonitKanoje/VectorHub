import { useState } from "react";

import OptionsButton from "./OptionsButton";

import YTModal from "./YTModal";
import VideoModal from "./VideoModal";
import AudioModal from "./AudioModal";
import TextModal from "./TextModal";

const Options = () => {
  const [activeModal, setActiveModal] = useState(null);

  return (
    <>
      <div className="w-56 flex flex-col gap-1">
        <OptionsButton
          text="Youtube Transcript"
          onClick={() => setActiveModal("Youtube Transcript")}
        />

        <OptionsButton
          text="Video Summary"
          onClick={() => setActiveModal("Video Summary")}
        />

        <OptionsButton
          text="Audio Summary"
          onClick={() => setActiveModal("Audio Summary")}
        />

        <OptionsButton
          text="Text Summary"
          onClick={() => setActiveModal("Text Summary")}
        />
      </div>

      {activeModal === "Youtube Transcript" && (
        <div
          className="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
          onClick={() => setActiveModal(null)}
        >
          <div onClick={(e) => e.stopPropagation()}>
            <YTModal />
          </div>
        </div>
      )}

      {activeModal === "Video Summary" && (
        <div
          className="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
          onClick={() => setActiveModal(null)}
        >
          <div onClick={(e) => e.stopPropagation()}>
            <VideoModal />
          </div>
        </div>
      )}

      {activeModal === "Audio Summary" && (
        <div
          className="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
          onClick={() => setActiveModal(null)}
        >
          <div onClick={(e) => e.stopPropagation()}>
            <AudioModal />
          </div>
        </div>
      )}

      {activeModal === "Text Summary" && (
        <div
          className="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
          onClick={() => setActiveModal(null)}
        >
          <div onClick={(e) => e.stopPropagation()}>
            <TextModal />
          </div>
        </div>
      )}
    </>
  );
};

export default Options;
