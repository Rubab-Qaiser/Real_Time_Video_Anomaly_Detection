const variants = {
  success: {
    bg: "bg-green-500/10",
    text: "text-green-400",
    border: "border-green-500/20",
    dot: "bg-green-400",
  },

  danger: {
    bg: "bg-red-500/10",
    text: "text-red-400",
    border: "border-red-500/20",
    dot: "bg-red-400",
  },

  warning: {
    bg: "bg-yellow-500/10",
    text: "text-yellow-400",
    border: "border-yellow-500/20",
    dot: "bg-yellow-400",
  },

  info: {
    bg: "bg-blue-500/10",
    text: "text-blue-400",
    border: "border-blue-500/20",
    dot: "bg-blue-400",
  },

  neutral: {
    bg: "bg-slate-700/30",
    text: "text-slate-300",
    border: "border-slate-600",
    dot: "bg-slate-400",
  },
};

export default function StatusBadge({
  children,
  variant = "neutral",
  showDot = true,
  className = "",
}) {
  const style = variants[variant] || variants.neutral;

  return (
    <span
      className={`
        inline-flex
        items-center
        gap-2
        rounded-full
        border
        px-3
        py-1
        text-xs
        font-semibold
        tracking-wide
        ${style.bg}
        ${style.text}
        ${style.border}
        ${className}
      `}
    >
      {showDot && (
        <span
          className={`
            h-2
            w-2
            rounded-full
            ${style.dot}
          `}
        />
      )}

      {children}
    </span>
  );
}