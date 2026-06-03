const OptionsButton = ({ text, onClick }) => {
  return (
    <button
      className="
        w-full
        text-left
        px-4
        py-3
        rounded-lg
        text-zinc-700
        hover:bg-zinc-100
        hover:text-black
        transition-all
        duration-150
        active:scale-[0.98]
      "
      onClick={onClick}
    >
      {text}
    </button>
  );
};

export default OptionsButton;
