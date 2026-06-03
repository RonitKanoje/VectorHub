const TextModal = () => {
  return (
    <div className="w-[420px] bg-white rounded-2xl shadow-2xl p-8 flex flex-col gap-6">
      <div>
        <h1 className="text-2xl font-bold text-zinc-900">Text Summary</h1>

        <p className="text-sm text-zinc-500 mt-1">
          Paste your text below and we'll generate a summary.
        </p>
      </div>

      <textarea
        placeholder="Paste your text here..."
        className="
          w-full
          h-48
          p-4
          border
          border-zinc-300
          rounded-lg
          resize-none
          focus:outline-none
          focus:ring-2
          focus:ring-violet-500
          focus:border-transparent
        "
      />

      <div className="flex justify-end">
        <button
          className="
            px-5
            py-2
            rounded-lg
            bg-violet-600
            text-white
            hover:bg-violet-700
            transition-all
            active:scale-95
          "
        >
          Submit
        </button>
      </div>
    </div>
  );
};

export default TextModal;
