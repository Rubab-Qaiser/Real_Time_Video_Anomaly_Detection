import { useSocket } from "@/contexts/SocketContext";
import { Wifi, WifiOff } from "lucide-react";

export default function SocketStatus() {
  const { isConnected } = useSocket();

  return (
    <div className="flex items-center gap-2 px-3 py-1.5 rounded-full border border-slate-700 bg-slate-800">
      {isConnected ? (
        <>
          <Wifi className="h-3.5 w-3.5 text-emerald-400" />
          <span className="text-xs text-slate-300">Live</span>
          <span className="relative flex h-2 w-2">
            <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-400 opacity-75"></span>
            <span className="relative inline-flex h-2 w-2 rounded-full bg-emerald-500"></span>
          </span>
        </>
      ) : (
        <>
          <WifiOff className="h-3.5 w-3.5 text-red-400" />
          <span className="text-xs text-slate-300">Offline</span>
        </>
      )}
    </div>
  );
}