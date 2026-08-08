export default function SkeletonCamera() {
  return (
    <div
      className="
        animate-pulse
        overflow-hidden
        rounded-2xl
        border
        border-slate-800
        bg-[#111827]
        shadow-lg
      "
    >
      {/* Header */}

      <div className="border-b border-slate-800 px-5 py-4">

        <div className="h-5 w-40 rounded bg-slate-700" />

        <div className="mt-3 h-3 w-56 rounded bg-slate-700" />

      </div>

      {/* Camera */}

      <div className="aspect-video bg-slate-800" />

      {/* Footer */}

      <div className="grid grid-cols-3 border-t border-slate-800">

        {[1, 2, 3].map((item) => (
          <div
            key={item}
            className="flex flex-col items-center py-4"
          >
            <div className="h-4 w-10 rounded bg-slate-700" />

            <div className="mt-2 h-3 w-16 rounded bg-slate-700" />
          </div>
        ))}

      </div>
    </div>
  );
}