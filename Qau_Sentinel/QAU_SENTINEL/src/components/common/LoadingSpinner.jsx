import { Loader2 } from "lucide-react";

export default function LoadingSpinner({
  text = "Loading...",
  fullScreen = false,
}) {
  const content = (
    <div className="flex flex-col items-center justify-center gap-4 py-10">
      <Loader2
        className="h-10 w-10 animate-spin text-blue-500"
      />

      <p className="text-sm text-slate-400">
        {text}
      </p>
    </div>
  );

  if (fullScreen) {
    return (
      <div className="flex min-h-[70vh] items-center justify-center">
        {content}
      </div>
    );
  }

  return content;
}