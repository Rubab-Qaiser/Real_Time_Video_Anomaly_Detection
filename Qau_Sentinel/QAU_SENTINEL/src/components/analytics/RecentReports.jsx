import {
  Flame,
  CloudFog,
  Users,
  Footprints,
  Activity,
  Swords,
  Package,
  ShieldAlert,
  Clock,
} from "lucide-react";

import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

import IncidentStatusBadge from "@/components/incidents/IncidentStatusBadge";

const ICON_BY_TYPE = {
  Fire: Flame,
  Smoke: CloudFog,
  Crowd: Users,
  Fall: Footprints,
  Running: Activity,
  Fight: Swords,
  "Unwanted Object": Package,
};

export default function RecentReports({ reports }) {
  if (!reports || reports.length === 0) {
    return (
      <Card className="border-slate-800 bg-slate-900">
        <CardHeader>
          <CardTitle className="text-white">Recent Reports</CardTitle>
        </CardHeader>
        <CardContent className="flex h-64 items-center justify-center text-slate-400">
          No reports available
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="border-slate-800 bg-slate-900">
      <CardHeader>
        <CardTitle className="text-white">Recent Reports</CardTitle>
      </CardHeader>

      <CardContent>
        <div className="space-y-3">
          {reports.map((report) => {
            const type = report.detection_type || report.type || "Unknown";
            const Icon = ICON_BY_TYPE[type] || ShieldAlert;
            const timestamp = report.timestamp
              ? new Date(report.timestamp).toLocaleString()
              : "Unknown";

            return (
              <div
                key={report.id}
                className="flex items-center justify-between rounded-lg border border-slate-800 bg-slate-950 p-4"
              >
                <div className="flex items-center gap-4">
                  <div className="rounded-lg bg-slate-800 p-3">
                    <Icon size={20} className="text-blue-400" />
                  </div>

                  <div>
                    <h4 className="font-medium text-white">{type}</h4>
                    <p className="text-sm text-slate-400">
                      {report.camera || "Camera"} — {report.location || "Unknown location"}
                    </p>
                    <div className="mt-1 flex items-center gap-2 text-xs text-slate-500">
                      <Clock size={12} />
                      {timestamp}
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  <IncidentStatusBadge status={report.status} />
                </div>
              </div>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
}
