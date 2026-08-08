import {
  Flame,
  Users,
  CheckCircle,
  Footprints,
  Activity,
  Swords,
  Package,
} from "lucide-react";

import StatusCard from "@/components/cards/StatusCard";

export default function IncidentStats({
  incidents = [],
}) {
  // Count incidents by type
  const fire = incidents.filter(
    (incident) => incident.type === "Fire"
  ).length;
  
  const crowd = incidents.filter(
    (incident) => incident.type === "Crowd"
  ).length;

  const fall = incidents.filter(
    (incident) => incident.type === "Fall"
  ).length;

  const running = incidents.filter(
    (incident) => incident.type === "Running"
  ).length;

  const fight = incidents.filter(
    (incident) => incident.type === "Fight"
  ).length;

  const unwantedObject = incidents.filter(
    (incident) => incident.type === "Unwanted Object"
  ).length;

  const resolved = incidents.filter(
    (incident) => incident.status === "Resolved"
  ).length;

  // Total incidents
  const total = fire + crowd + fall + running + fight + unwantedObject;

  return (
    <div
      className="
        grid
        gap-4
        grid-cols-1
        sm:grid-cols-2
        lg:grid-cols-3
        xl:grid-cols-4
        2xl:grid-cols-4
      "
    >
      <StatusCard
        title="Fire Alerts"
        value={fire}
        icon={Flame}
        iconColor="text-red-500"
      />

      <StatusCard
        title="Crowd Alerts"
        value={crowd}
        icon={Users}
        iconColor="text-sky-400"
      />

      <StatusCard
        title="Fall Alerts"
        value={fall}
        icon={Footprints}
        iconColor="text-orange-400"
      />

      <StatusCard
        title="Running Alerts"
        value={running}
        icon={Activity}
        iconColor="text-purple-400"
      />

      <StatusCard
        title="Fight Alerts"
        value={fight}
        icon={Swords}
        iconColor="text-red-400"
      />

      <StatusCard
        title="Unwanted Objects"
        value={unwantedObject}
        icon={Package}
        iconColor="text-amber-400"
      />

      <StatusCard
        title="Total Incidents"
        value={total}
        icon={CheckCircle}
        iconColor="text-blue-400"
      />

      <StatusCard
        title="Resolved"
        value={resolved}
        icon={CheckCircle}
        iconColor="text-emerald-400"
      />
    </div>
  );
}