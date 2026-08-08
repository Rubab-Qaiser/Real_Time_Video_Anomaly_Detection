import { AlertTriangle, RotateCcw } from "lucide-react";

import { Button } from "@/components/ui/button";

export default function ErrorState({
  title = "Something went wrong",
  description = "Unable to load data.",
  onRetry,
}) {
  return (
    <div className="flex flex-col items-center justify-center rounded-xl border border-red-900/40 bg-red-950/20 px-6 py-12 text-center">

      <AlertTriangle className="h-12 w-12 text-red-500" />

      <h2 className="mt-5 text-xl font-semibold text-white">
        {title}
      </h2>

      <p className="mt-2 max-w-md text-sm text-slate-400">
        {description}
      </p>

      {onRetry && (
        <Button
          className="mt-6"
          variant="destructive"
          onClick={onRetry}
        >
          <RotateCcw className="mr-2 h-4 w-4" />

          Try Again
        </Button>
      )}

    </div>
  );
}