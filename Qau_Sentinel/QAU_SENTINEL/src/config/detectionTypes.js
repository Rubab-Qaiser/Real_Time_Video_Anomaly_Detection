// src/config/detectionTypes.js

import {
  Flame,
  Users,
  Footprints,
  Activity,
  Swords,
  Package,
  AlertTriangle,
} from "lucide-react";

export const DETECTION_TYPES = {
  fire: {
    id: "fire",
    label: "Fire",
    icon: Flame,
    iconColor: "text-red-500",
    bgColor: "bg-red-500/15",
    borderColor: "border-red-500/30",
    textColor: "text-red-400",
    severity: "critical",
  },
  crowd: {
    id: "crowd",
    label: "Crowd",
    icon: Users,
    iconColor: "text-sky-400",
    bgColor: "bg-sky-500/15",
    borderColor: "border-sky-500/30",
    textColor: "text-sky-400",
    severity: "medium",
  },
  fall: {
    id: "fall",
    label: "Fall",
    icon: Footprints,
    iconColor: "text-orange-400",
    bgColor: "bg-orange-500/15",
    borderColor: "border-orange-500/30",
    textColor: "text-orange-400",
    severity: "critical",
  },
  running: {
    id: "running",
    label: "Running",
    icon: Activity,
    iconColor: "text-purple-400",
    bgColor: "bg-purple-500/15",
    borderColor: "border-purple-500/30",
    textColor: "text-purple-400",
    severity: "high",
  },
  fight: {
    id: "fight",
    label: "Fight",
    icon: Swords,
    iconColor: "text-red-400",
    bgColor: "bg-red-500/15",
    borderColor: "border-red-500/30",
    textColor: "text-red-400",
    severity: "critical",
  },
  unwanted_object: {
    id: "unwanted_object",
    label: "Unwanted Object",
    icon: Package,
    iconColor: "text-amber-400",
    bgColor: "bg-amber-500/15",
    borderColor: "border-amber-500/30",
    textColor: "text-amber-400",
    severity: "high",
  },
};

// Get detection type config by key
export function getDetectionType(type) {
  if (!type) return null;
  const key = type.toLowerCase();
  return DETECTION_TYPES[key] || {
    id: key,
    label: type,
    icon: AlertTriangle,
    iconColor: "text-gray-400",
    bgColor: "bg-gray-500/15",
    borderColor: "border-gray-500/30",
    textColor: "text-gray-400",
    severity: "unknown",
  };
}

// Get all detection types as an array
export function getDetectionTypeList() {
  return Object.values(DETECTION_TYPES);
}

// Get detection types for filters (label + value)
export function getDetectionFilterOptions() {
  return Object.values(DETECTION_TYPES).map((type) => ({
    value: type.id,
    label: type.label,
    icon: type.icon,
  }));
}

// Check if a type exists
export function isValidDetectionType(type) {
  if (!type) return false;
  return !!DETECTION_TYPES[type.toLowerCase()];
}