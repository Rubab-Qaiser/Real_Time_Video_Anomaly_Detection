import { Badge } from "@/components/ui/badge";

const STATUS_STYLES = {
  Open: "bg-red-500/15 text-red-400 border-red-500/30",
  Investigating: "bg-amber-500/15 text-amber-400 border-amber-500/30",
  Resolved: "bg-emerald-500/15 text-emerald-400 border-emerald-500/30",
  Acknowledged: "bg-blue-500/15 text-blue-400 border-blue-500/30",
  Assigned: "bg-purple-500/15 text-purple-400 border-purple-500/30",
  Closed: "bg-slate-500/15 text-slate-400 border-slate-500/30",
};

export default function IncidentStatusBadge({ status }) {
  const style = STATUS_STYLES[status] || STATUS_STYLES.Open;
  
  return (
    <Badge variant="outline" className={style}>
      {status}
    </Badge>
  );
}