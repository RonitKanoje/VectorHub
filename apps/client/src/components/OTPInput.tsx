import { useRef } from "react";

interface OTPInputProps {
  otp: string[];
  setOtp: (otp: string[]) => void;
  length?: number;
}

const OTPInput = ({ otp, setOtp, length = 6 }: OTPInputProps) => {
  const inputRefs = useRef<(HTMLInputElement | null)[]>([]);

  const handleChange = (index: number, value: string) => {
    if (!/^\d?$/.test(value)) return;

    const newOtp = [...otp];
    newOtp[index] = value;
    setOtp(newOtp);

    // Move to next input
    if (value && index < length - 1) {
      inputRefs.current[index + 1]?.focus();
    }
  };

  const handleKeyDown = (
    index: number,
    e: React.KeyboardEvent<HTMLInputElement>,
  ) => {
    // Move back on backspace
    if (e.key === "Backspace" && otp[index] === "" && index > 0) {
      inputRefs.current[index - 1]?.focus();
    }
  };

  return (
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
  );
};

export default OTPInput;
