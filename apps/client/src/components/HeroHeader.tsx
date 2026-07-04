const HeroHeader = () => {
  return (
    <div className="text-center mb-8 relative z-10">
      <h1 className="text-4xl md:text-5xl font-black tracking-tight text-white">
        Vector
        <span className="bg-clip-text text-transparent bg-gradient-to-r from-[#ff007f]  to-[#7000ff]">
          Hub
        </span>
      </h1>
      <p className="text-xs text-zinc-500 mt-2 font-semibold tracking-widest uppercase">
        Your AI Assistant
      </p>
    </div>
  );
};

export default HeroHeader;
