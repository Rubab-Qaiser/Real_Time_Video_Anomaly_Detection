import { Badge } from "@/components/ui/badge";

const SEVERITY_STYLES = {
  critical: "bg-red-600/20 text-red-400 border-red-600/30",
  high: "bg-orange-600/20 text-orange-400 border-orange-600/30",
  medium: "bg-yellow-600/20 text-yellow-400 border-yellow-600/30",
  low: "bg-blue-600/20 text-blue-400 border-blue-600/30",
  unknown: "bg-slate-600/20 text-slate-400 border-slate-600/30",
};

export default function SeverityBadge({ severity }) {
  const key = severity?.trim().toLowerCase() || "unknown";

  return (
    <Badge
      variant="outline"
      className={SEVERITY_STYLES[key] || SEVERITY_STYLES.unknown}
    >
      {severity || "Unknown"}
    </Badge>
  );
}