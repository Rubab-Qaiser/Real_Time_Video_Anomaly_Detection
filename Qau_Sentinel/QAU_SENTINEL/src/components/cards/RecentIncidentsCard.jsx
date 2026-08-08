import {
  Flame,
  CloudFog,
  Users,
  ChevronRight,
} from "lucide-react";

import StatusBadge from "@/components/common/StatusBadge";

const STATUS_VARIANT = {
  Open: "danger",
  Resolved: "success",
  Active: "warning",
};

const STATUS_LABEL = {
  Open: "Open",
  Resolved: "Resolved",
  Active: "Active",
};

const ICON_BY_TYPE = {
  Fire: Flame,
  Smoke: CloudFog,
  Crowd: Users,
  Fight: Flame,
  Fall: Flame,
  Running: Users,
  "Unwanted Object": Users,
};

export default function RecentIncidentsCard({ incidents = [] }) {
  const latestIncidents = incidents.slice(0, 3);

  return (
    <div className="rounded-2xl border border-slate-800 bg-[#111827] shadow-lg">

      {/* ==========================================
          Header
      ========================================== */}

      <div className="flex items-center justify-between border-b border-slate-800 px-5 py-4">

        <div>

          <h2 className="text-lg font-semibold text-white">
            Recent Incidents
          </h2>

          <p className="mt-1 text-sm text-slate-400">
            Latest AI detected events
          </p>

        </div>

        <button
          className="
            flex
            items-center
            gap-1
            text-sm
            text-blue-400
            transition
            hover:text-blue-300
          "
        >
          View All

          <ChevronRight size={16} />
        </button>

      </div>

      {/* ==========================================
          Incident List
      ========================================== */}

      <div className="divide-y divide-slate-800">

        {latestIncidents.length === 0 ? (
          <div className="px-5 py-6 text-sm text-slate-400">
            Waiting for live incidents...
          </div>
        ) : (
          latestIncidents.map((incident) => {
            const Icon = ICON_BY_TYPE[incident.type] || Flame;
            const variant = STATUS_VARIANT[incident.status] || "warning";
            const timeLabel = incident.timestamp
              ? new Date(incident.timestamp).toLocaleTimeString([], {
                  hour: "2-digit",
                  minute: "2-digit",
                })
              : "Just now";

            return (
              <div
                key={incident.id}
                className="
                  flex
                  items-center
                  justify-between
                  px-5
                  py-4
                  transition
                  hover:bg-slate-800/40
                "
              >
                <div className="flex items-center gap-4">
                  <div className="rounded-xl bg-slate-800 p-3">
                    <Icon
                      size={20}
                      className={
                        variant === "danger"
                          ? "text-red-400"
                          : variant === "warning"
                          ? "text-yellow-400"
                          : "text-green-400"
                      }
                    />
                  </div>

                  <div>
                    <h3 className="font-medium text-white">
                      {incident.type || incident.detection_type}
                    </h3>
                    <p className="mt-1 text-sm text-slate-400">
                      {incident.camera || incident.location || "Camera"}
                    </p>
                  </div>
                </div>

                <div className="text-right">
                  <StatusBadge variant={variant}>
                    {STATUS_LABEL[incident.status] || incident.status || "Open"}
                  </StatusBadge>
                  <p className="mt-2 text-xs text-slate-500">{timeLabel}</p>
                </div>
              </div>
            );
          })
        )}

      </div>

    </div>
  );
}