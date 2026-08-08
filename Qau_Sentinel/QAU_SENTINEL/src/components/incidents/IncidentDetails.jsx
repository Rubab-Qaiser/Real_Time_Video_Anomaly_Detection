import {
  Flame,
  CloudFog,
  Users,
  Camera,
  MapPin,
  ShieldAlert,
  ExternalLink,
} from "lucide-react";

import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet";

import IncidentTimeline from "./IncidentTimeline";
import IncidentStatusBadge from "./IncidentStatusBadge";

const ICONS = {
  Fire: Flame,
  Smoke: CloudFog,
  Crowd: Users,
};

const COLORS = {
  Fire: "text-red-500",
  Smoke: "text-yellow-400",
  Crowd: "text-sky-400",
};

const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:5000/api";

export default function IncidentDetails({
  open,
  onOpenChange,
  incident,
}) {
  if (!incident) return null;

  const Icon = ICONS[incident.type] || ShieldAlert;
  const snapshotUrl = incident.frame_path
    ? `${API_BASE}/alerts/${encodeURIComponent(incident.frame_path.split(/[\\/]/).pop())}`
    : null;

  return (
    <Sheet
      open={open}
      onOpenChange={onOpenChange}
    >
      <SheetContent
        side="right"
        className="w-full overflow-y-auto border-slate-800 bg-slate-950 sm:max-w-xl"
      >
        <SheetHeader>

          <SheetTitle className="flex items-center gap-2 text-white">

            <Icon
              size={22}
              className={COLORS[incident.type]}
            />

            {incident.type} Incident

          </SheetTitle>

        </SheetHeader>

        <div className="mt-6 space-y-6">

          {/* Thumbnail - Show snapshot if available */}
          {snapshotUrl ? (
            <div className="relative aspect-video overflow-hidden rounded-lg border border-slate-800 bg-slate-900">
              <img
                src={snapshotUrl}
                alt={`${incident.type} incident snapshot`}
                className="h-full w-full object-cover"
                onError={(e) => {
                  console.error(`[IncidentDetails] Failed to load snapshot image: ${snapshotUrl}`);
                  e.target.style.display = "none";
                  e.target.parentElement.innerHTML = `
                    <div class="flex aspect-video items-center justify-center rounded-lg border border-slate-800 bg-slate-900">
                      <svg class="text-slate-600" width="60" height="60" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M14.5 4h-5L7 7H4a2 2 0 0 0-2 2v9a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V9a2 2 0 0 0-2-2h-3l-2.5-3z"/>
                        <circle cx="12" cy="13" r="3"/>
                      </svg>
                    </div>
                  `;
                }}
              />
              <a
                href={snapshotUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="absolute bottom-2 right-2 rounded-lg bg-slate-900/80 p-2 text-white transition hover:bg-slate-700"
              >
                <ExternalLink size={16} />
              </a>
            </div>
          ) : (
            <div className="flex aspect-video items-center justify-center rounded-lg border border-slate-800 bg-slate-900">
              <Camera size={60} className="text-slate-600" />
            </div>
          )}

          {/* Information */}

          <div className="grid gap-4">

            <Info
              label="Incident ID"
              value={incident.id}
            />

            <Info
              label="Camera"
              value={incident.camera}
            />

            <Info
              label="Location"
              value={incident.location}
              icon={MapPin}
            />

            <Info
              label="Detection Confidence"
              value={`${incident.confidence}%`}
            />

            <Info
              label="Severity"
              value={incident.severity}
            />

            <div>

              <p className="mb-2 text-sm text-slate-400">
                Status
              </p>

              <IncidentStatusBadge
                status={incident.status}
              />

            </div>

          </div>

          <IncidentTimeline />

        </div>

      </SheetContent>
    </Sheet>
  );
}

function Info({
  label,
  value,
  icon: Icon,
}) {
  return (
    <div className="rounded-lg border border-slate-800 bg-slate-900 p-4">

      <p className="mb-2 text-sm text-slate-400">
        {label}
      </p>

      <div className="flex items-center gap-2">

        {Icon && (
          <Icon
            size={16}
            className="text-blue-400"
          />
        )}

        <span className="font-medium text-white">
          {value}
        </span>

      </div>

    </div>
  );
}