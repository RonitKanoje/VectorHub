interface AuthFooterProps {
  question: string;
  linkText: string;
  onLinkClick: () => void;
}


const AuthFooter = ({ question, linkText, onLinkClick }: AuthFooterProps) => {
  return (
    <div className="mt-6 text-center">
      <p className="text-zinc-500 text-xs">{question}</p>
      <button
        className="mt-2 text-[#00f0ff] hover:text-[#00f0ff]/80 font-bold text-xs hover:underline transition-colors cursor-pointer"
        onClick={onLinkClick}
      >
        {linkText}
      </button>
    </div>
  );
};

export default AuthFooter;
