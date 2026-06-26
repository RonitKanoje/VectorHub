import { BarChart2, Sparkles, TableProperties } from "lucide-react";

interface EmptyStateProps {
  isAnalystMode?: boolean;
}

const EmptyState = ({ isAnalystMode = false }: EmptyStateProps) => {
  if (isAnalystMode) {
    return (
      <div className="mx-auto flex h-full max-w-2xl flex-col items-center justify-center py-20 text-center">
        {/* <div className="mb-5 flex h-16 w-16 items-center justify-center rounded-2xl bg-violet-600/20 text-violet-400">
          <TableProperties className="h-8 w-8" />
        </div> */}
        <h1 className="text-3xl font-bold text-white">
          Let's Analyse the data
        </h1>
        {/* <p className="mt-3 max-w-md text-sm leading-6 text-slate-400">
          Upload a <strong className="text-violet-400">CSV or Excel file</strong> using the +
          button below, then ask questions. The multi-agent pipeline will preprocess your data,
          detect outliers, generate insights, and return meaningful analysis.
        </p> */}
      </div>
    );
  }

  return (
    <div className="mx-auto flex h-full max-w-3xl flex-col items-center justify-center text-center py-16">
      <div className="mb-5 flex h-14 w-14 items-center justify-center rounded-2xl bg-cyan-100 dark:bg-cyan-900/40 text-cyan-700 dark:text-cyan-300">
        <Sparkles className="h-7 w-7" />
      </div>
      <h1 className="text-3xl font-bold tracking-tight text-slate-950 dark:text-white">
        Ask normally, or add content for RAG.
      </h1>
      <p className="mt-3 max-w-xl text-sm leading-6 text-slate-500 dark:text-slate-400">
        General questions work immediately. Use the plus button when you want
        this chat to answer from YouTube, audio, video, or text chunks.
      </p>
    </div>
  );
};

export default EmptyState;
