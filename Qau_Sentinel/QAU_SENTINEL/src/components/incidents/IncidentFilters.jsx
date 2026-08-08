import { useState } from "react";
import { Search, Filter, X } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

import { getDetectionFilterOptions } from "@/config/detectionTypes";

const SEVERITY_OPTIONS = [
  { value: "all", label: "All Severities" },
  { value: "critical", label: "Critical" },
  { value: "high", label: "High" },
  { value: "medium", label: "Medium" },
  { value: "low", label: "Low" },
];

const STATUS_OPTIONS = [
  { value: "all", label: "All Statuses" },
  { value: "Open", label: "Open" },
  { value: "Investigating", label: "Investigating" },
  { value: "Resolved", label: "Resolved" },
  { value: "Acknowledged", label: "Acknowledged" },
  { value: "Assigned", label: "Assigned" },
];

export default function IncidentFilters({
  search = "",
  onSearchChange,
  type = "all",
  onTypeChange,
  severity = "all",
  onSeverityChange,
  status = "all",
  onStatusChange,
  onReset,
}) {
  const [isExpanded, setIsExpanded] = useState(false);

  const typeOptions = getDetectionFilterOptions();

  const handleReset = () => {
    onSearchChange("");
    onTypeChange("all");
    onSeverityChange("all");
    onStatusChange("all");
    if (onReset) onReset();
  };

  return (
    <div className="space-y-4">
      {/* Main Filter Bar */}
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
        {/* Search */}
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-500" />
          <Input
            placeholder="Search incidents..."
            value={search}
            onChange={(e) => onSearchChange(e.target.value)}
            className="pl-9 bg-slate-900 border-slate-700 text-white placeholder:text-slate-500"
          />
        </div>

        {/* Type Filter */}
        <div className="w-full sm:w-44">
          <Select value={type} onValueChange={onTypeChange}>
            <SelectTrigger className="bg-slate-900 border-slate-700 text-white">
              <SelectValue placeholder="All Types" />
            </SelectTrigger>
            <SelectContent className="bg-slate-900 border-slate-700 text-white">
              <SelectItem value="all">All Types</SelectItem>
              {typeOptions.map((option) => (
                <SelectItem key={option.value} value={option.value}>
                  {option.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        {/* Toggle Advanced Filters */}
        <Button
          variant="outline"
          size="sm"
          onClick={() => setIsExpanded(!isExpanded)}
          className="border-slate-700 text-slate-400 hover:bg-slate-800 hover:text-white"
        >
          <Filter className="mr-2 h-4 w-4" />
          {isExpanded ? "Less Filters" : "More Filters"}
        </Button>

        {/* Reset */}
        {(search || type !== "all" || severity !== "all" || status !== "all") && (
          <Button
            variant="ghost"
            size="sm"
            onClick={handleReset}
            className="text-slate-400 hover:text-white hover:bg-slate-800"
          >
            <X className="mr-2 h-4 w-4" />
            Reset
          </Button>
        )}
      </div>

      {/* Advanced Filters */}
      {isExpanded && (
        <div className="flex flex-wrap gap-3 pt-2 border-t border-slate-800">
          {/* Severity Filter */}
          <div className="w-full sm:w-44">
            <Select value={severity} onValueChange={onSeverityChange}>
              <SelectTrigger className="bg-slate-900 border-slate-700 text-white">
                <SelectValue placeholder="All Severities" />
              </SelectTrigger>
              <SelectContent className="bg-slate-900 border-slate-700 text-white">
                {SEVERITY_OPTIONS.map((option) => (
                  <SelectItem key={option.value} value={option.value}>
                    {option.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Status Filter */}
          <div className="w-full sm:w-44">
            <Select value={status} onValueChange={onStatusChange}>
              <SelectTrigger className="bg-slate-900 border-slate-700 text-white">
                <SelectValue placeholder="All Statuses" />
              </SelectTrigger>
              <SelectContent className="bg-slate-900 border-slate-700 text-white">
                {STATUS_OPTIONS.map((option) => (
                  <SelectItem key={option.value} value={option.value}>
                    {option.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </div>
      )}
    </div>
  );
}