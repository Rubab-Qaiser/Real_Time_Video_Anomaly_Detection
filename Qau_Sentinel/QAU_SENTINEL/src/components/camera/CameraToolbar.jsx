import { Plus, RefreshCw } from "lucide-react";

import { Button } from "@/components/ui/button";

export default function CameraToolbar({
  search = "",
  onSearchChange,
  status = "all",
  onStatusChange,
  onRefresh,
  onAddCamera,
}) {
  return (
    <div className="flex flex-col gap-4 rounded-xl border border-slate-800 bg-slate-900 p-4 lg:flex-row lg:items-center lg:justify-between">
      <div className="flex flex-1 gap-3">
        {/* Search */}
        <input
          type="text"
          value={search}
          onChange={(e) => onSearchChange(e.target.value)}
          placeholder="Search cameras..."
          className="flex-1 rounded-lg border border-slate-700 bg-slate-950 px-4 py-2 text-white focus:outline-none focus:border-blue-500"
        />

        {/* Status Filter */}
        <select
          value={status}
          onChange={(e) => onStatusChange(e.target.value)}
          className="rounded-lg border border-slate-700 bg-slate-950 px-4 text-white"
        >
          <option value="all">All Status</option>
          <option value="Online">Online</option>
          <option value="Offline">Offline</option>
          <option value="Maintenance">Maintenance</option>
        </select>
      </div>

      <div className="flex gap-2">
        <Button variant="outline" onClick={onRefresh}>
          <RefreshCw className="mr-2 h-4 w-4" />
          Refresh
        </Button>

        <Button onClick={onAddCamera}>
          <Plus className="mr-2 h-4 w-4" />
          Add Camera
        </Button>
      </div>
    </div>
  );
}