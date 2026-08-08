import { motion } from "framer-motion";

export default function LivePulse({
  label = "LIVE",
  color = "bg-emerald-500",
  textColor = "text-emerald-400",
  className = "",
}) {
  return (
    <div
      className={`flex items-center gap-2 ${className}`}
    >
      <motion.span
        className={`h-2.5 w-2.5 rounded-full ${color}`}
        animate={{
          scale: [1, 1.35, 1],
          opacity: [1, 0.5, 1],
        }}
        transition={{
          duration: 1.4,
          repeat: Infinity,
          ease: "easeInOut",
        }}
      />

      <span
        className={`text-sm font-medium ${textColor}`}
      >
        {label}
      </span>
    </div>
  );
}