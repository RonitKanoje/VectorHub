const Home = () => {
  return (
    <div className="min-h-screen bg-black flex flex-col justify-center items-center px-4 relative overflow-hidden">
      {/* Decorative background grid for depth */}

      {/* Headline outside the box */}
      <div className="text-center mb-8 relative z-10">
        <h1 className="text-4xl md:text-5xl font-black tracking-tight text-white">
          vector
          <span className="bg-clip-text text-transparent bg-gradient-to-r from-[#ff007f]  to-[#7000ff]">
            Hub
          </span>
        </h1>
        <p className="text-xs text-zinc-500 mt-2 font-semibold tracking-widest uppercase">
          Next-Gen Vector Intelligence Portal
        </p>
      </div>

      {/* Animated RGB Card Container */}
      <div className="relative w-full max-w-[580px] group">
        {/* Rear Glow Shadow (creates the subtle RGB glow on the page) */}
        {/* <div className="absolute inset-0 bg-[conic-gradient(from_0deg,#ff007f,#00f0ff,#7000ff,#ff007f)] rounded-2xl blur-xl opacity-80 animate-spin [animation-duration:10s]" /> */}

        {/* Border Container */}
        <div className="relative rounded-2xl p-[1.5px] overflow-hidden bg-zinc-900">
          {/* Rotating RGB Border Effect */}
          <div className="absolute inset-[-100%] bg-[conic-gradient(from_0deg,#ff007f,#00f0ff,#7000ff,#ff007f)] animate-spin [animation-duration:3s]" />

          {/* Inner Card (Dark Box) */}
          <div className="relative bg-[#09090b] rounded-[15px] p-8 z-10 w-full flex flex-col">
            {/* Header inside the box */}
            <div className="text-center mb-8">
              <h2 className="text-xl font-bold text-white tracking-tight">
                Welcome Back
              </h2>
              <p className="text-xs text-zinc-400 mt-1">
                Enter your credentials to access your console
              </p>
            </div>

            {/* Inputs & Actions */}
            <div className="flex flex-col gap-4">
              <input
                type="text"
                placeholder="Username"
                className="w-full h-12 px-4 bg-[#121214] border border-zinc-800 rounded-xl focus:outline-none focus:ring-1 focus:ring-[#00f0ff] focus:border-[#00f0ff] transition-all duration-200 placeholder-zinc-600 text-white text-sm"
              />

              <input
                type="password"
                placeholder="Password"
                className="w-full h-12 px-4 bg-[#121214] border border-zinc-800 rounded-xl focus:outline-none focus:ring-1 focus:ring-[#00f0ff] focus:border-[#00f0ff] transition-all duration-200 placeholder-zinc-600 text-white text-sm"
              />

              {/* Login Button */}
              <button className="w-full h-12 bg-white text-black hover:bg-zinc-200 font-bold rounded-xl transition-all duration-200 active:scale-[0.95] cursor-pointer text-sm">
                Login
              </button>
            </div>

            {/* Footer inside the box */}
            <div className="mt-6 text-center">
              <p className="text-zinc-500 text-xs">Don't have an account?</p>
              <button className="mt-2 text-[#00f0ff] hover:text-[#00f0ff]/80 font-bold text-xs hover:underline transition-colors cursor-pointer">
                Register now
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Home;
