import { Flame, CloudFog, Users } from "lucide-react";

const COLORS = {
  red: {
    border: "border-red-500",
    background: "bg-red-500",
    text: "text-red-400",
  },

  yellow: {
    border: "border-yellow-400",
    background: "bg-yellow-400",
    text: "text-yellow-300",
  },

  blue: {
    border: "border-sky-500",
    background: "bg-sky-500",
    text: "text-sky-400",
  },
};

const ICONS = {
  Fire: Flame,
  Smoke: CloudFog,
  Crowd: Users,
};

export default function DetectionBox({ detection }) {
  const style = COLORS[detection.color] || COLORS.red;

  const Icon = ICONS[detection.label];

  return (
    <div
      className={`
        absolute
        border-2
        ${style.border}
        rounded-md
        shadow-lg
        pointer-events-none
        animate-pulse
      `}
      style={{
        left: `${detection.x}%`,
        top: `${detection.y}%`,
        width: `${detection.width}%`,
        height: `${detection.height}%`,
      }}
    >
      {/* Detection Label */}

      <div
        className={`
          absolute
          -top-8
          left-0
          flex
          items-center
          gap-1
          rounded-md
          px-2
          py-1
          text-xs
          font-semibold
          text-white
          ${style.background}
          whitespace-nowrap
        `}
      >
        {Icon && <Icon size={14} />}

        <span>{detection.label}</span>

        <span>{detection.confidence}%</span>
      </div>
    </div>
  );
}