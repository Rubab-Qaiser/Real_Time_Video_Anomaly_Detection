import { useState } from "react";

import {
  Card,
  CardContent,
} from "@/components/ui/card";

import {
  Table,
  TableBody,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

import IncidentRow from "./IncidentRow";
import IncidentDetails from "./IncidentDetails";

export default function IncidentTable({
  incidents = [],
}) {
  const [selectedIncident, setSelectedIncident] = useState(null);
  const [open, setOpen] = useState(false);

  function handleView(incident) {
    setSelectedIncident(incident);
    setOpen(true);
  }

  return (
    <>
      <Card className="border-slate-800 bg-slate-900">
        <CardContent className="p-0">
          <div className="overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>ID</TableHead>
                  <TableHead>Time</TableHead>
                  <TableHead>Camera</TableHead>
                  <TableHead>Location</TableHead>
                  <TableHead>Type</TableHead>
                  <TableHead>Confidence</TableHead>
                  <TableHead>Severity</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead className="text-right">
                    Action
                  </TableHead>
                </TableRow>
              </TableHeader>

              <TableBody>
                {incidents.map((incident) => (
                  <IncidentRow
                    key={incident.id}
                    incident={incident}
                    onView={handleView}
                  />
                ))}
              </TableBody>
            </Table>
          </div>
        </CardContent>
      </Card>

      <IncidentDetails
        incident={selectedIncident}
        open={open}
        onOpenChange={setOpen}
      />
    </>
  );
}