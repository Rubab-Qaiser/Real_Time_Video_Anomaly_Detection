import {
  Search,
  Filter,
  Download,
  RefreshCw,
} from "lucide-react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

export default function IncidentToolbar({
  search = "",
  onSearchChange,
  type = "all",
  onTypeChange,
  onRefresh,
  onExport,
}) {
  return (
    <div className="flex flex-col gap-3 rounded-xl border border-slate-800 bg-slate-900 p-4 lg:flex-row lg:items-center lg:justify-between">
      {/* Left Side */}
      <div className="flex flex-1 flex-col gap-3 md:flex-row">
        {/* Search */}
        <div className="relative w-full md:max-w-sm">
          <Search size={18} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
          <Input
            value={search}
            onChange={(e) => onSearchChange(e.target.value)}
            placeholder="Search incidents..."
            className="border-slate-700 bg-slate-950 pl-10 text-white placeholder:text-slate-500"
          />
        </div>

        {/* Filter */}
        <div className="relative">
          <Filter size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
          <select
            value={type}
            onChange={(e) => onTypeChange(e.target.value)}
            className="h-10 rounded-md border border-slate-700 bg-slate-950 pl-9 pr-8 text-sm text-white outline-none"
          >
            <option value="all">All Incidents</option>
            <option value="fire">Fire</option>
            <option value="smoke">Smoke</option>
            <option value="crowd">Crowd</option>
          </select>
        </div>
      </div>

      {/* Right Side */}
      <div className="flex gap-2">
        <Button variant="outline" className="border-slate-700" onClick={onRefresh}>
          <RefreshCw className="mr-2 h-4 w-4" />
          Refresh
        </Button>

        {/* Export Dropdown */}
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button>
              <Download className="mr-2 h-4 w-4" />
              Export
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuItem onClick={() => onExport("csv")}>
              Export as CSV
            </DropdownMenuItem>
            <DropdownMenuItem onClick={() => onExport("excel")}>
              Export as Excel
            </DropdownMenuItem>
            <DropdownMenuItem onClick={() => onExport("pdf")}>
              Export as PDF
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </div>
  );
}