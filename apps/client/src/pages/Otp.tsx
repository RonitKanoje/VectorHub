import { useRef, useState } from "react";

const Otp = () => {
  const [otp, setOtp] = useState(["", "", "", "", "", ""]);  ///// for storing the 6 digits of the OTP
  const inputRefs = useRef([]);

  const handleChange = (index, value) => {
    if (!/^\d?$/.test(value)) return;

    const newOtp = [...otp];
    newOtp[index] = value;
    setOtp(newOtp);

    // Move to next input
    if (value && index < otp.length - 1) {
      inputRefs.current[index + 1]?.focus();
    }
  };

  const handleKeyDown = (index, e) => {
    // Move back on backspace
    if (e.key === "Backspace" && otp[index] === "" && index > 0) {
      inputRefs.current[index - 1]?.focus();
    }
  };

  const handleSubmit = () => {
    const finalOtp = otp.join("");
    console.log(finalOtp);
  };

  return (
    <div className="bg-mist-800 text-white h-screen flex justify-center items-center">
      <div className="bg-mist-700 p-8 rounded-xl shadow-lg">
        <h1 className="text-3xl font-bold text-center">OTP Verification</h1>

        <p className="text-center mt-2 text-gray-300">
          Enter the OTP sent to your email
        </p>

        <div className="flex gap-3 mt-6 justify-center">
          {otp.map((digit, index) => (
            <input
              key={index}
              ref={(el) => (inputRefs.current[index] = el)}
              type="text"
              maxLength={1}
              value={digit}
              onChange={(e) => handleChange(index, e.target.value)}
              onKeyDown={(e) => handleKeyDown(index, e)}
              className="
                w-12 h-12
                text-center
                text-xl
                rounded-lg
                border
                border-gray-500
                bg-mist-600
                focus:outline-none
                focus:ring-2
                focus:ring-blue-500
              "
            />
          ))}
        </div>

        <button
          onClick={handleSubmit}
          className="
            mt-6
            w-full
            h-12
            bg-blue-600
            rounded-lg
            hover:bg-blue-700
            transition
            active:scale-95
          "
        >
          Verify OTP
        </button>
      </div>
    </div>
  );
};

export default Otp;
