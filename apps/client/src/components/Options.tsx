import OptionsButton from "./OptionsButton";

const Options = () => {
  return (
    <div className="w-[200px] h-[170px] bg-zinc-400 rounded-lg p-4">
      <OptionsButton text="Youtube Transcript" />
      <OptionsButton text="Video Summary" />
      <OptionsButton text="Audio Summary" />
      <OptionsButton text="Text Summary" />
    </div>
  );
};

export default Options;
