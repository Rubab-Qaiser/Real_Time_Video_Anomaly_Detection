import {
  Flame,
  CloudFog,
  Users,
} from "lucide-react";

const ITEMS = [
  {
    label: "Fire",
    color: "bg-red-500",
    icon: Flame,
  },
  {
    label: "Smoke",
    color: "bg-yellow-400",
    icon: CloudFog,
  },
  {
    label: "Crowd",
    color: "bg-sky-500",
    icon: Users,
  },
];

export default function DetectionLegend() {
  return (
    <div
      className="
        absolute
        bottom-4
        left-4
        z-30
        rounded-xl
        border
        border-slate-700
        bg-slate-900/90
        px-4
        py-3
        backdrop-blur-md
      "
    >
      <h4 className="mb-3 text-sm font-semibold text-white">
        Detection Legend
      </h4>

      <div className="flex flex-wrap gap-3">

        {ITEMS.map(({ label, color, icon: Icon }) => (
          <div
            key={label}
            className="flex items-center gap-2"
          >
            <span
              className={`flex h-6 w-6 items-center justify-center rounded-full ${color}`}
            >
              <Icon
                size={14}
                className="text-white"
              />
            </span>

            <span className="text-sm text-slate-300">
              {label}
            </span>
          </div>
        ))}

      </div>
    </div>
  );
}