import {
  AlertTriangle,
  Camera,
  Brain,
  Target,
} from "lucide-react";

import StatusCard from "@/components/cards/StatusCard";

export default function AnalyticsOverview({ data }) {
  const {
    totalIncidents,
    activeCameras,
    averageConfidence,
    aiAccuracy,
  } = data;

  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
      <StatusCard
        title="Total Incidents"
        value={totalIncidents}
        icon={AlertTriangle}
        iconColor="text-red-500"
      />

<StatusCard
        title="Total Cameras"
        value={activeCameras}
        icon={Camera}
        iconColor="text-blue-500"
      />

      <StatusCard
        title="Avg. Confidence"
        value={`${averageConfidence}%`}
        icon={Brain}
        iconColor="text-violet-500"
      />

      <StatusCard
        title="AI Accuracy"
        value={`${aiAccuracy}%`}
        icon={Target}
        iconColor="text-emerald-500"
      />
    </div>
  );
}