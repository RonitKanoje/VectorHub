import { TableProperties } from "lucide-react";

const SUGGESTED_PROMPTS = [
  "Show me the top 5 rows",
  "What are the outliers?",
  "Give me a statistical summary",
  "Plot sales by region",
];

interface AnalystEmptyStateProps {
  onSelectPrompt: (prompt: string) => void;
}

const AnalystEmptyState = ({ onSelectPrompt }: AnalystEmptyStateProps) => {
  return (
    <div className="mx-auto flex max-w-2xl flex-col items-center justify-center py-20 text-center">
      <div className="mb-5 flex h-16 w-16 items-center justify-center rounded-2xl bg-violet-600/20 text-violet-400">
        <TableProperties className="h-8 w-8" />
      </div>
      <h1 className="text-3xl font-bold text-white">Data Analyst Agent</h1>
      <p className="mt-3 max-w-md text-sm leading-6 text-slate-400">
        Upload a <strong className="text-violet-400">CSV or Excel file</strong> using the +
        button below, then ask questions. The multi-agent pipeline will preprocess your data,
        detect outliers, generate insights, and return meaningful analysis.
      </p>
      <div className="mt-6 flex gap-3 flex-wrap justify-center">
        {SUGGESTED_PROMPTS.map((q) => (
          <button
            key={q}
            onClick={() => onSelectPrompt(q)}
            className="rounded-xl border border-slate-700 bg-slate-800 px-3 py-1.5 text-xs text-slate-300 hover:border-violet-600 hover:text-violet-400 transition"
          >
            {q}
          </button>
        ))}
      </div>
    </div>
  );
};

export default AnalystEmptyState;