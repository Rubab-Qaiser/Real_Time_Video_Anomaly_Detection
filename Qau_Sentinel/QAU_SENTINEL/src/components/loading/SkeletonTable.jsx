export default function SkeletonTable({
  rows = 6,
  columns = 5,
}) {
  return (
    <div className="overflow-hidden rounded-2xl border border-slate-800 bg-[#111827] shadow-lg">

      {/* Header */}

      <div className="border-b border-slate-800 px-6 py-4">
        <div className="h-5 w-48 animate-pulse rounded bg-slate-700" />
      </div>

      {/* Table */}

      <div className="divide-y divide-slate-800">

        {Array.from({ length: rows }).map((_, row) => (

          <div
            key={row}
            className="grid gap-4 px-6 py-4"
            style={{
              gridTemplateColumns: `repeat(${columns}, minmax(0,1fr))`,
            }}
          >

            {Array.from({ length: columns }).map((_, column) => (

              <div
                key={column}
                className="h-4 animate-pulse rounded bg-slate-700"
              />

            ))}

          </div>

        ))}

      </div>

    </div>
  );
}