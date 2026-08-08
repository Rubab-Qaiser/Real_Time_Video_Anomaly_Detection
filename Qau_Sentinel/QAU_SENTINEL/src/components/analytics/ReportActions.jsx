import {
  Download,
  FileText,
  FileSpreadsheet,
  FileBarChart2,
} from "lucide-react";

import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

import { Button } from "@/components/ui/button";
import { getAccessToken } from "@/utils/token";

const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:5000/api";

export default function ReportActions() {
  const handleGeneratePDF = () => {
    const token = getAccessToken();
    const url = `${API_BASE}/analytics/export/pdf?token=${encodeURIComponent(token)}&t=${Date.now()}`;
    window.open(url, "_blank");
  };

  const handleGenerateCSV = () => {
    const token = getAccessToken();
    const url = `${API_BASE}/analytics/export/csv?token=${encodeURIComponent(token)}&t=${Date.now()}`;
    window.open(url, "_blank");
  };

  const handleGenerateSummary = () => {
    const token = getAccessToken();
    const url = `${API_BASE}/analytics/export/csv?token=${encodeURIComponent(token)}&t=${Date.now()}`;
    window.open(url, "_blank");
  };

  return (
    <Card className="border-slate-800 bg-slate-900">
      <CardHeader>
        <CardTitle className="text-white">
          Report Actions
        </CardTitle>
      </CardHeader>

      <CardContent>

        <div className="grid gap-4 sm:grid-cols-3">

          <Button
            className="h-16 flex-col gap-2"
            onClick={handleGeneratePDF}
          >
            <FileText size={22} />
            Export PDF
          </Button>

          <Button
            variant="secondary"
            className="h-16 flex-col gap-2"
            onClick={handleGenerateCSV}
          >
            <FileSpreadsheet size={22} />
            Export CSV
          </Button>

          <Button
            variant="outline"
            className="h-16 flex-col gap-2 border-slate-700"
            onClick={handleGenerateSummary}
          >
            <FileBarChart2 size={22} />
            AI Summary
          </Button>

        </div>

        <div className="mt-5 rounded-lg border border-dashed border-slate-700 p-4">

          <div className="flex items-center gap-2 text-slate-400">

            <Download size={18} />

            <span className="text-sm">
              Reports generated here will later be downloaded
              directly from the Flask backend.
            </span>

          </div>

        </div>

      </CardContent>
    </Card>
  );
}