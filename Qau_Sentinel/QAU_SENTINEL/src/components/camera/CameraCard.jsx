import { useEffect, useRef, useState } from "react";
import { Camera, Wifi, WifiOff, Circle, Maximize2, Edit3, Trash2, MapPin, Play, Pause, RefreshCw } from "lucide-react";

import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

import { FadeIn, LivePulse } from "@/components/animations";
import { getAccessToken } from "@/utils/token";

export default function CameraCard({ camera, onEdit, onDelete }) {
  const [isPlaying, setIsPlaying] = useState(false);
  const [streamUrl, setStreamUrl] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const previewRef = useRef(null);
  const imgRef = useRef(null);

  const statusConfig = {
    Online: { label: "Online", color: "text-emerald-400", icon: <Wifi size={16} /> },
    Offline: { label: "Offline", color: "text-red-400", icon: <WifiOff size={16} /> },
    Maintenance: { label: "Maintenance", color: "text-amber-400", icon: <Circle size={12} fill="currentColor" /> },
  };

  const status = statusConfig[camera.status] || statusConfig.Offline;
  const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:5000/api";
  const REMOTE_STREAM_URL = import.meta.env.VITE_REMOTE_STREAM_URL || "http://localhost:8080/stream";

  const buildStreamUrl = (token, preferredSource = "remote") => {
    const cacheBuster = `t=${Date.now()}`;

    if (preferredSource === "remote" && REMOTE_STREAM_URL) {
      const separator = REMOTE_STREAM_URL.includes("?") ? "&" : "?";
      return `${REMOTE_STREAM_URL}${separator}${cacheBuster}`;
    }

    const tokenQuery = token ? `token=${encodeURIComponent(token)}` : "";
    const queryPrefix = tokenQuery ? `?${tokenQuery}` : "";
    const additionalSeparator = tokenQuery ? "&" : "?";
    return `${API_BASE}/cameras/${camera.id}/live${queryPrefix}${additionalSeparator}${cacheBuster}`;
  };

  useEffect(() => {
    if (!isPlaying) { setIsLoading(false); setStreamUrl(""); setError(""); return; }
    setIsLoading(true); setError("");
    const token = getAccessToken();
    if (!token) { setError("Please log in to view the live stream."); setIsLoading(false); return; }
    setStreamUrl(buildStreamUrl(token, "remote"));
    const timer = window.setTimeout(() => setIsLoading(false), 8000);
    return () => window.clearTimeout(timer);
  }, [API_BASE, camera.id, isPlaying, REMOTE_STREAM_URL]);

  const handleToggleStream = () => setIsPlaying((prev) => !prev);

  const handleRefresh = () => {
    setError(""); setIsLoading(true);
    const token = getAccessToken();
    if (!token) { setError("Please log in to view the live stream."); setIsLoading(false); return; }
    setStreamUrl("");
    setTimeout(() => setStreamUrl(buildStreamUrl(token, "remote")), 50);
  };

  const handleStreamError = () => {
    const token = getAccessToken();
    if (!token) {
      setIsLoading(false);
      setError("Please log in to view the live stream.");
      return;
    }

    if (streamUrl.includes("localhost:8080/stream")) {
      setIsLoading(true);
      setError("Primary stream unavailable. Retrying backend stream...");
      setStreamUrl("");
      setTimeout(() => setStreamUrl(buildStreamUrl(token, "backend")), 80);
      return;
    }

    setIsLoading(false);
    setError("Unable to connect to the camera stream right now.");
  };

  const toggleFullscreen = () => {
    if (!previewRef.current) return;
    if (!document.fullscreenElement) { previewRef.current.requestFullscreen?.(); }
    else { document.exitFullscreen?.(); }
  };

  return (
    <FadeIn>
      <Card className="overflow-hidden border-slate-800 bg-slate-900 transition-all duration-300 hover:-translate-y-1 hover:border-slate-700 hover:shadow-xl">
        <div ref={previewRef} className="relative aspect-video bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
          {isPlaying && streamUrl ? (
            <>
              <img ref={imgRef} src={streamUrl} alt={`${camera.name} live stream`}
                className="h-full w-full object-contain"
                onLoad={() => { setIsLoading(false); setError(""); }}
                onError={handleStreamError} />
              {isLoading && (
                <div className="absolute inset-0 z-10 flex flex-col items-center justify-center bg-slate-900/80">
                  <div className="h-8 w-8 animate-spin rounded-full border-4 border-blue-500 border-t-transparent" />
                  <p className="mt-3 text-sm text-slate-300">Connecting...</p>
                </div>
              )}
            </>
          ) : (
            <div className="absolute inset-0 flex flex-col items-center justify-center">
              <Camera size={60} className="mb-3 text-slate-600" />
              <p className="font-medium text-slate-300">Live Stream</p>
              <p className="mt-1 text-xs text-slate-500">{isPlaying ? "Preparing preview..." : "Click play to view the live feed"}</p>
            </div>
          )}
          {error && (
            <div className="absolute inset-0 z-10 flex flex-col items-center justify-center bg-slate-900/90 px-4 text-center">
              <p className="text-sm text-red-400">{error}</p>
              <Button variant="secondary" size="sm" className="mt-3" onClick={handleRefresh}>
                <RefreshCw className="mr-2 h-4 w-4" /> Retry
              </Button>
            </div>
          )}
          {camera.status === "Online" && (
            <div className="absolute left-3 top-3"><LivePulse /></div>
          )}
          <div className="absolute right-3 top-3 flex items-center gap-2">
            <Button size="icon" variant="secondary" className="bg-slate-900/80 hover:bg-slate-700" onClick={toggleFullscreen}>
              <Maximize2 size={16} />
            </Button>
          </div>
          <div className="absolute bottom-3 left-3 flex items-center gap-2">
            <Button size="sm" variant={isPlaying ? "destructive" : "secondary"} className="bg-slate-900/80 hover:bg-slate-700" onClick={handleToggleStream}>
              {isPlaying ? <Pause className="mr-2 h-4 w-4" /> : <Play className="mr-2 h-4 w-4" />}
              {isPlaying ? "Pause" : "Play"}
            </Button>
          </div>
        </div>

        <CardContent className="space-y-4 p-4">
          <div className="flex items-start justify-between">
            <div>
              <h3 className="text-lg font-semibold text-white">{camera.name}</h3>
              <div className="mt-1 flex items-center gap-1 text-sm text-slate-400">
                <MapPin size={14} /> {camera.location}
              </div>
            </div>
            <div className={"flex items-center gap-1 text-sm font-medium " + status.color}>
              {status.icon} {status.label}
            </div>
          </div>

          <div className="grid grid-cols-3 gap-2 border-t border-slate-800 pt-3">
            <div className="text-center">
              <p className="text-xs text-slate-500">Resolution</p>
              <p className="text-sm font-semibold text-white">{camera.resolution ? (camera.resolution.split("x").pop() + "p") : "N/A"}</p>
            </div>
            <div className="text-center">
              <p className="text-xs text-slate-500">FPS</p>
              <p className="text-sm font-semibold text-white">{camera.fps ?? "N/A"}</p>
            </div>
            <div className="text-center">
              <p className="text-xs text-slate-500">AI Status</p>
              <p className={"text-sm font-semibold " + (camera.ai_status === "Active" ? "text-emerald-400" : camera.ai_status === "Idle" ? "text-amber-400" : "text-slate-400")}>
                {camera.ai_status || "N/A"}
              </p>
            </div>
          </div>

          <div className="flex gap-2 pt-2">
            <Button variant="outline" size="sm" className="flex-1 border-slate-700" onClick={() => onEdit(camera)}>
              <Edit3 className="mr-2 h-4 w-4" /> Edit
            </Button>
            <Button variant="destructive" size="sm" className="flex-1" onClick={() => onDelete(camera)}>
              <Trash2 className="mr-2 h-4 w-4" /> Delete
            </Button>
          </div>
        </CardContent>
      </Card>
    </FadeIn>
  );
}
