import { TableProperties } from "lucide-react";
import type { AnalystUploadedDataset } from "../types/analyst";

interface AnalystDatasetPillsProps {
  datasets: AnalystUploadedDataset[];
}

const AnalystDatasetPills = ({ datasets }: AnalystDatasetPillsProps) => {
  if (datasets.length === 0) return null;

  return (
    <div className="border-t border-slate-800 bg-slate-900 px-4 py-2">
      <div className="mx-auto flex max-w-4xl flex-wrap gap-1.5">
        {datasets.map((d) => (
          <span
            key={d.id}
            className="flex items-center gap-1.5 rounded-full border border-violet-800 bg-violet-900/30 px-2.5 py-1 text-xs text-violet-300"
          >
            <TableProperties className="h-3 w-3" />
            {d.name}
          </span>
        ))}
      </div>
    </div>
  );
};

export default AnalystDatasetPills;