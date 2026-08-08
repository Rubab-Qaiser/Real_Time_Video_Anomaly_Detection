import SkeletonCard from "./SkeletonCard";
import SkeletonCamera from "./SkeletonCamera";
import SkeletonTable from "./SkeletonTable";

export default function SkeletonDashboard() {
  return (
    <div className="flex flex-col gap-5">

      {/* Page Header */}

      <div>

        <div className="h-8 w-64 animate-pulse rounded bg-slate-700" />

        <div className="mt-3 h-4 w-96 animate-pulse rounded bg-slate-700" />

      </div>

      {/* Status Cards */}

      <section className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">

        <SkeletonCard />
        <SkeletonCard />
        <SkeletonCard />
        <SkeletonCard />

      </section>

      {/* Main Area */}

      <section className="grid grid-cols-1 gap-5 xl:grid-cols-12">

        <div className="xl:col-span-8">
          <SkeletonCamera />
        </div>

        <div className="xl:col-span-4">
          <SkeletonTable
            rows={6}
            columns={2}
          />
        </div>

      </section>

      {/* Bottom */}

      <section className="grid grid-cols-1 gap-5 xl:grid-cols-2">

        <SkeletonTable
          rows={4}
          columns={3}
        />

        <SkeletonTable
          rows={4}
          columns={3}
        />

      </section>

    </div>
  );
}