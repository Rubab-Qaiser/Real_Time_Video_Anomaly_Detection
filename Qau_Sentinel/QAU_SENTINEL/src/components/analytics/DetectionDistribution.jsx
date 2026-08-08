import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

import {
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Tooltip,
  Legend,
} from "recharts";

const COLORS = ["#ef4444", "#facc15", "#38bdf8"];

export default function DetectionDistribution({ data }) {
  if (!data || data.length === 0) {
    return (
      <Card className="border-slate-800 bg-slate-900 h-full">
        <CardHeader>
          <CardTitle className="text-white">Detection Distribution</CardTitle>
        </CardHeader>
        <CardContent className="flex h-[350px] items-center justify-center text-slate-400">
          No detection distribution data available
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="border-slate-800 bg-slate-900 h-full">
      <CardHeader>
        <CardTitle className="text-white">Detection Distribution</CardTitle>
      </CardHeader>

      <CardContent>
        <div className="h-[350px]">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={data}
                dataKey="value"
                nameKey="name"
                outerRadius={120}
                label
              >
                {data.map((_, index) => (
                  <Cell
                    key={index}
                    fill={COLORS[index % COLORS.length]}
                  />
                ))}
              </Pie>

              <Tooltip />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  );
}