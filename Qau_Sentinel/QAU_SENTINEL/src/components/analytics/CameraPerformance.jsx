import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

export default function CameraPerformance({ data }) {
  if (!data || data.length === 0) {
    return (
      <Card className="border-slate-800 bg-slate-900">
        <CardHeader>
          <CardTitle className="text-white">Camera Performance</CardTitle>
        </CardHeader>
        <CardContent className="flex h-64 items-center justify-center text-slate-400">
          No camera performance data available
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="border-slate-800 bg-slate-900">
      <CardHeader>
        <CardTitle className="text-white">Camera Performance</CardTitle>
      </CardHeader>

      <CardContent className="p-0">
        <div className="overflow-x-auto">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Camera</TableHead>
                <TableHead>Location</TableHead>
                <TableHead>Uptime</TableHead>
                <TableHead>Incidents</TableHead>
                <TableHead>AI Confidence</TableHead>
              </TableRow>
            </TableHeader>

            <TableBody>
              {data.map((camera) => (
                <TableRow key={camera.id}>
                  <TableCell className="font-medium">{camera.camera}</TableCell>
                  <TableCell>{camera.location}</TableCell>
                  <TableCell>{camera.uptime}%</TableCell>
                  <TableCell>{camera.incidents}</TableCell>
                  <TableCell>{camera.confidence}%</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      </CardContent>
    </Card>
  );
}