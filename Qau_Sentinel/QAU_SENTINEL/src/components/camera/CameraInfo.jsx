import {
  Activity,
  Monitor,
  Wifi,
  Clock,
  Bot,
  MapPin,
} from "lucide-react";

import { Card } from "@/components/ui/card";

export default function CameraInfo({
  camera = {
    name: "Main Entrance",
    location: "Gate A",
    resolution: "1920 × 1080",
    fps: 30,
    latency: "24 ms",
    aiStatus: "Ready",
    streamStatus: "Connected",
  },
}) {
  return (
    <Card className="border-slate-800 bg-slate-900 p-5">

      <h3 className="mb-5 text-lg font-semibold text-white">
        Camera Information
      </h3>

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">

        <InfoItem
          icon={Monitor}
          label="Resolution"
          value={camera.resolution}
        />

        <InfoItem
          icon={Activity}
          label="Frame Rate"
          value={`${camera.fps} FPS`}
        />

        <InfoItem
          icon={Wifi}
          label="Stream"
          value={camera.streamStatus}
          valueColor="text-emerald-400"
        />

        <InfoItem
          icon={Clock}
          label="Latency"
          value={camera.latency}
        />

        <InfoItem
          icon={Bot}
          label="AI Engine"
          value={camera.aiStatus}
          valueColor="text-blue-400"
        />

        <InfoItem
          icon={MapPin}
          label="Location"
          value={camera.location}
        />

      </div>

    </Card>
  );
}

function InfoItem({
  icon: Icon,
  label,
  value,
  valueColor = "text-white",
}) {
  return (
    <div className="rounded-lg border border-slate-800 bg-slate-950 p-4">

      <div className="mb-3 flex items-center gap-2">

        <Icon
          size={18}
          className="text-blue-400"
        />

        <span className="text-sm text-slate-400">
          {label}
        </span>

      </div>

      <p className={`font-semibold ${valueColor}`}>
        {value}
      </p>

    </div>
  );
}