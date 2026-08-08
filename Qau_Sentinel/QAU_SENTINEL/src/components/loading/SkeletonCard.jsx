export default function SkeletonCard() {
  return (
    <div
      className="
        animate-pulse
        rounded-2xl
        border
        border-slate-800
        bg-[#111827]
        p-5
        shadow-lg
      "
    >
      {/* Icon + Title */}

      <div className="flex items-center justify-between">

        <div>

          <div className="h-4 w-28 rounded bg-slate-700" />

          <div className="mt-3 h-8 w-20 rounded bg-slate-700" />

        </div>

        <div className="h-12 w-12 rounded-xl bg-slate-700" />

      </div>

      {/* Footer */}

      <div className="mt-6 h-3 w-36 rounded bg-slate-700" />
    </div>
  );
}