const YTModal = () => {
  return (
    <div className="w-[420px] bg-white rounded-2xl shadow-2xl p-8 flex flex-col gap-6">
      <div>
        <h1 className="text-2xl font-bold text-zinc-900">YouTube Transcript</h1>

        <p className="text-sm text-zinc-500 mt-1">
          Paste a YouTube URL and we'll process it for you.
        </p>
      </div>

      <input
        type="text"
        placeholder="https://youtube.com/watch?v=..."
        className="
          w-full
          h-12
          px-4
          border
          border-zinc-300
          rounded-lg
          focus:outline-none
          focus:ring-2
          focus:ring-violet-500
          focus:border-transparent
        "
      />

      <div className="flex justify-end gap-3">
        <button
          className="
            px-4
            py-2
            rounded-lg
            border
            border-zinc-300
            text-zinc-700
            hover:bg-zinc-100
            transition
          "
        >
          Cancel
        </button>

        <button
          className="
            px-5
            py-2
            rounded-lg
            bg-black
            text-white
            hover:bg-violet-700
            active:scale-95
            transition-all
          "
        >
          Submit
        </button>
      </div>
    </div>
  );
};

export default YTModal;
