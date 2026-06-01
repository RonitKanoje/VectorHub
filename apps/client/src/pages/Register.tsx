const Register = () => {
  return (
    <div className="min-h-screen bg-black flex flex-col justify-center items-center px-4 relative overflow-hidden">
      {/* Decorative background grid for depth */}
      <div className="absolute inset-0 bg-[linear-gradient(to_right,#1f293708_1px,transparent_1px),linear-gradient(to_bottom,#1f293708_1px,transparent_1px)] bg-[size:4rem_4rem] [mask-image:radial-gradient(ellipse_60%_50%_at_50%_50%,#000_70%,transparent_100%)] pointer-events-none" />

      {/* Animated RGB Card Container (Increased max width to 480px) */}
      <div className="relative w-full max-w-[580px] group">
        {/* Rear Glow Shadow */}
        <div className="absolute inset-0 bg-[conic-gradient(from_0deg,#ff007f,#00f0ff,#7000ff,#ff007f)] rounded-2xl blur-xl opacity-10 animate-spin [animation-duration:10s]" />

        {/* Border Container */}
        <div className="relative rounded-2xl p-[1.5px] overflow-hidden bg-zinc-900">
          {/* Rotating RGB Border Effect */}
          <div className="absolute inset-[-100%] bg-[conic-gradient(from_0deg,#ff007f,#00f0ff,#7000ff,#ff007f)] animate-spin [animation-duration:6s]" />

          {/* Inner Card (Dark Box) */}
          <div className="relative bg-[#09090b] rounded-[15px] p-8 md:p-10 z-10 w-full flex flex-col">
            {/* Header inside the box */}
            <div className="text-center mb-8">
              <h2 className="text-2xl font-bold text-white tracking-tight">
                Create Account
              </h2>
              <p className="text-xs text-zinc-400 mt-1">
                Get started with your developer workspace
              </p>
            </div>

            {/* Inputs & Actions */}
            <div className="flex flex-col gap-4">
              <input
                type="text"
                placeholder="Full Name"
                className="w-full h-12 px-4 bg-[#121214] border border-zinc-800 rounded-xl focus:outline-none focus:ring-1 focus:ring-[#00f0ff] focus:border-[#00f0ff] transition-all duration-200 placeholder-zinc-600 text-white text-sm"
              />

              <input
                type="email"
                placeholder="Email Address"
                className="w-full h-12 px-4 bg-[#121214] border border-zinc-800 rounded-xl focus:outline-none focus:ring-1 focus:ring-[#00f0ff] focus:border-[#00f0ff] transition-all duration-200 placeholder-zinc-600 text-white text-sm"
              />

              {/* Side-by-side passwords for a wider, different layout */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <input
                  type="password"
                  placeholder="Password"
                  className="w-full h-12 px-4 bg-[#121214] border border-zinc-800 rounded-xl focus:outline-none focus:ring-1 focus:ring-[#00f0ff] focus:border-[#00f0ff] transition-all duration-200 placeholder-zinc-600 text-white text-sm"
                />
                <input
                  type="password"
                  placeholder="Confirm Password"
                  className="w-full h-12 px-4 bg-[#121214] border border-zinc-800 rounded-xl focus:outline-none focus:ring-1 focus:ring-[#00f0ff] focus:border-[#00f0ff] transition-all duration-200 placeholder-zinc-600 text-white text-sm"
                />
              </div>

              {/* Create Account Button */}
              <button className="w-full h-12 bg-white text-black hover:bg-zinc-200 font-bold rounded-xl transition-all duration-200 active:scale-[0.97] cursor-pointer text-sm mt-2">
                Create Account
              </button>
            </div>

            {/* Footer inside the box */}
            <div className="mt-6 text-center">
              <p className="text-zinc-500 text-xs">Already have an account?</p>
              <button className="mt-2 text-[#00f0ff] hover:text-[#00f0ff]/80 font-bold text-xs hover:underline transition-colors cursor-pointer">
                Sign in
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Register;
