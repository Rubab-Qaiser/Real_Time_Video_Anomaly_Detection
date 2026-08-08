import { Eye } from "lucide-react";

import { Button } from "@/components/ui/button";
import {
  TableCell,
  TableRow,
} from "@/components/ui/table";

import IncidentStatusBadge from "./IncidentStatusBadge";
import SeverityBadge from "./SeverityBadge";
import { getDetectionType } from "@/config/detectionTypes";

export default function IncidentRow({
  incident,
  onView,
}) {
  const config = getDetectionType(incident.type);
  const Icon = config?.icon;

  return (
    <TableRow className="hover:bg-slate-900/50">

      <TableCell className="font-medium">
        {incident.id}
      </TableCell>

      <TableCell>
        {incident.timestamp}
      </TableCell>

      <TableCell>
        {incident.camera}
      </TableCell>

      <TableCell>
        {incident.location}
      </TableCell>

      <TableCell>
        <div className={`flex items-center gap-2 ${config?.iconColor || "text-gray-400"}`}>
          {Icon && <Icon size={16} />}
          {config?.label || incident.type}
        </div>
      </TableCell>

      <TableCell>
        {incident.confidence}%
      </TableCell>

      <TableCell>
        <SeverityBadge severity={incident.severity} />
      </TableCell>

      <TableCell>
        <IncidentStatusBadge status={incident.status} />
      </TableCell>

      <TableCell className="text-right">
        <Button
          size="sm"
          variant="outline"
          onClick={() => onView(incident)}
        >
          <Eye className="mr-2 h-4 w-4" />
          View
        </Button>
      </TableCell>

    </TableRow>
  );
}