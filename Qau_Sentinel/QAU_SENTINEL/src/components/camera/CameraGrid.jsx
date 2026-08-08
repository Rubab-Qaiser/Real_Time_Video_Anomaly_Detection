import CameraCard from "./CameraCard";

export default function CameraGrid({ cameras, onEdit, onDelete }) {
  if (!cameras || cameras.length === 0) {
    return (
      <div className="rounded-xl border border-slate-800 bg-slate-900 py-16 text-center">
        <p className="text-slate-400">No cameras found matching your criteria.</p>
      </div>
    );
  }

  return (
    <section className="grid grid-cols-1 gap-5 md:grid-cols-2 xl:grid-cols-3 2xl:grid-cols-4">
      {cameras.map((camera) => (
        <CameraCard
          key={camera.id}
          camera={camera}
          onEdit={onEdit}
          onDelete={onDelete}
        />
      ))}
    </section>
  );
}