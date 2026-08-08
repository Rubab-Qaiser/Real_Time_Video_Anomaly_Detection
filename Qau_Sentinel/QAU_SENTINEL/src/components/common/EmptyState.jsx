import { Inbox } from "lucide-react";

import { Button } from "@/components/ui/button";

export default function EmptyState({
  icon: Icon = Inbox,
  title = "Nothing here",
  description = "No data available.",
  actionLabel,
  onAction,
}) {
  return (
    <div className="flex flex-col items-center justify-center rounded-xl border border-dashed border-slate-700 bg-slate-900 px-6 py-12 text-center">

      <div className="rounded-full bg-slate-800 p-4">
        <Icon className="h-10 w-10 text-slate-400" />
      </div>

      <h2 className="mt-6 text-xl font-semibold text-white">
        {title}
      </h2>

      <p className="mt-2 max-w-md text-sm text-slate-400">
        {description}
      </p>

      {actionLabel && (
        <Button
          className="mt-6"
          onClick={onAction}
        >
          {actionLabel}
        </Button>
      )}

    </div>
  );
}