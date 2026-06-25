import { TableProperties } from "lucide-react";

const AnalystEmptyState = () => {
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
    </div>
  );
};

export default AnalystEmptyState;