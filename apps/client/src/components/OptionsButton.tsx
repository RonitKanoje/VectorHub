const OptionsButton = ({ text }) => {
  return (
    <div>
      <button className="w-full  hover:bg-zinc-800 text-white text-sm font-medium py-2 px-4 rounded-xl transition-all active:scale-[0.98] cursor-pointer">
        {text}
      </button>
    </div>
  );
};

export default OptionsButton;
