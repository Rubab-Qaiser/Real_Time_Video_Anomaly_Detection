import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

import {
  ResponsiveContainer,
  LineChart,
  Line,
  CartesianGrid,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
} from "recharts";

export default function MonthlyTrendChart({ data }) {
  // Safeguard: Ensure data is always an array
  const chartData = Array.isArray(data) ? data : [];

  if (chartData.length === 0) {
    return (
      <Card className="border-slate-800 bg-slate-900">
        <CardContent className="flex h-[350px] items-center justify-center text-slate-400">
          No monthly trend data available
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="border-slate-800 bg-slate-900 h-full">
      <CardHeader>
        <CardTitle className="text-white">Monthly Incident Trend</CardTitle>
      </CardHeader>

      <CardContent>
        <div className="h-[350px]">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" />

              <XAxis dataKey="month" stroke="#94a3b8" />

              <YAxis stroke="#94a3b8" />

              <Tooltip />

              <Legend />

              <Line
                type="monotone"
                dataKey="Fire"
                stroke="#ef4444"
                strokeWidth={3}
              />
              <Line
                type="monotone"
                dataKey="Smoke"
                stroke="#facc15"
                strokeWidth={3}
              />
              <Line
                type="monotone"
                dataKey="Crowd"
                stroke="#38bdf8"
                strokeWidth={3}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  );
}