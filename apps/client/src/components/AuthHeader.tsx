interface AuthHeaderProps {
  title: string;
  subtitle: string;
}

const AuthHeader = ({ title, subtitle }: AuthHeaderProps) => {
  return (
    <div className="text-center mb-8">
      <h2 className="text-2xl font-bold text-white tracking-tight">{title}</h2>
      <p className="text-xs text-zinc-400 mt-1">{subtitle}</p>
    </div>
  );
};

export default AuthHeader;
