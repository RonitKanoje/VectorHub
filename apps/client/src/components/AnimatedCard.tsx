interface AnimatedCardProps {
  children: React.ReactNode;
}

const AnimatedCard = ({ children }: AnimatedCardProps) => {
  return (
    <div className="relative w-full max-w-[580px] group">
      {/* Border Container */}
      <div className="relative rounded-2xl p-[1.5px] overflow-hidden bg-zinc-900">
        {/* Rotating RGB Border Effect */}
        <div className="absolute inset-[-100%] bg-[conic-gradient(from_0deg,#ff007f,#00f0ff,#7000ff,#ff007f)] animate-spin [animation-duration:3s]" />

        {/* Inner Card (Dark Box) */}
        <div className="relative bg-[#09090b] rounded-[15px] p-8 md:p-10 z-10 w-full flex flex-col">
          {children}
        </div>
      </div>
    </div>
  );
};

export default AnimatedCard;
