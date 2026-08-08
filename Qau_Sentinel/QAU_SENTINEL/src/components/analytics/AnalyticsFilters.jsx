import { useState } from "react";
import {
  Calendar,
  Camera,
  Download,
  Filter,
} from "lucide-react";

import { Button } from "@/components/ui/button";
import useCameras from "@/hooks/useCameras";
import { getAccessToken } from "@/utils/token";

const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:5000/api";

export default function AnalyticsFilters({ onFilterChange }) {
  const [range, setRange] = useState("7days");
  const [camera, setCamera] = useState("all");
  const { cameras, loading: camerasLoading } = useCameras();

  const handleApply = () => {
    if (onFilterChange) {
      onFilterChange({ range, camera });
    }
  };

  const handleExportReport = () => {
    const token = getAccessToken();
    const url = `${API_BASE}/analytics/export/csv?token=${encodeURIComponent(token)}&t=${Date.now()}`;
    window.open(url, "_blank");
  };

  return (
    <div
      className="
        flex
        flex-col
        gap-3
        rounded-xl
        border
        border-slate-800
        bg-slate-900
        p-4
        lg:flex-row
        lg:items-center
        lg:justify-between
      "
    >
      {/* Left */}

      <div className="flex flex-1 flex-col gap-3 md:flex-row">

        {/* Date Range */}

        <div className="relative">

          <Calendar
            size={16}
            className="
              absolute
              left-3
              top-1/2
              -translate-y-1/2
              text-slate-400
            "
          />

          <select
            value={range}
            onChange={(e) => setRange(e.target.value)}
            className="
              h-10
              rounded-md
              border
              border-slate-700
              bg-slate-950
              pl-9
              pr-8
              text-sm
              text-white
              outline-none
            "
          >
            <option value="today">Today</option>
            <option value="7days">Last 7 Days</option>
            <option value="30days">Last 30 Days</option>
            <option value="90days">Last 90 Days</option>
          </select>

        </div>

        {/* Camera */}

        <div className="relative">

          <Camera
            size={16}
            className="
              absolute
              left-3
              top-1/2
              -translate-y-1/2
              text-slate-400
            "
          />

          <select
            value={camera}
            onChange={(e) => setCamera(e.target.value)}
            className="
              h-10
              rounded-md
              border
              border-slate-700
              bg-slate-950
              pl-9
              pr-8
              text-sm
              text-white
              outline-none
            "
          >
            <option value="all">All Cameras</option>
            {camerasLoading ? (
              <option value="" disabled>Loading...</option>
            ) : (
              cameras?.map((cam) => (
                <option key={cam.id} value={String(cam.id)}>
                  {cam.name} ({cam.location})
                </option>
              ))
            )}
          </select>

        </div>

      </div>

      {/* Right */}

      <div className="flex gap-2">

        <Button
          variant="outline"
          className="border-slate-700"
          onClick={handleApply}
        >
          <Filter className="mr-2 h-4 w-4" />
          Apply
        </Button>

        <Button onClick={handleExportReport}>

          <Download className="mr-2 h-4 w-4" />

          Export Report

        </Button>

      </div>

    </div>
  );
}
