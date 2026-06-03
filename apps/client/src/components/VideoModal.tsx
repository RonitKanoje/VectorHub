import { useRef } from "react";

const VideoModal = () => {
  const fileInputRef = useRef(null);

  return (
    <div className="w-[420px] bg-white rounded-2xl shadow-2xl p-8 flex flex-col gap-6">
      <div>
        <h1 className="text-2xl font-bold text-zinc-900">Upload Video</h1>

        <p className="text-sm text-zinc-500 mt-1">
          Upload a video file to generate a summary.
        </p>
      </div>

      {/* Hidden file input */}
      <input
        ref={fileInputRef}
        type="file"
        accept="video/*"
        className="hidden"
      />

      <button
        className="
          w-full
          h-12
          border-2
          border-dashed
          border-zinc-300
          rounded-lg
          text-zinc-600
          hover:border-violet-500
          hover:text-violet-600
          transition-all
        "
        onClick={() => fileInputRef.current.click()}
      >
        Choose a File
      </button>

      <button
        className="
          w-full
          h-12
          bg-violet-600
          text-white
          rounded-lg
          hover:bg-violet-700
          transition-all
          active:scale-95
        "
      >
        Submit
      </button>
    </div>
  );
};

export default VideoModal;
