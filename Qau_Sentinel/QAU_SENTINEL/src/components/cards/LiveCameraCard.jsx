import { useState, useEffect, useRef } from "react";
import {
  Camera,
  Maximize2,
  RefreshCw,
} from "lucide-react";

import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

import {
  FadeIn,
  LivePulse,
} from "@/components/animations";

import { getAccessToken } from "@/utils/token";
import useCameras from "@/hooks/useCameras";

export default function LiveCameraCard({ cameraId = 1 }) {
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [streamUrl, setStreamUrl] = useState("");
  const [selectedCameraId, setSelectedCameraId] = useState(cameraId);
  const imgRef = useRef(null);
  const containerRef = useRef(null);

  const { cameras, loading: camerasLoading } = useCameras();
  const selectedCamera = cameras?.find(c => c.id === selectedCameraId);

  // Get API base URL from environment
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
    const separator = tokenQuery ? "&" : "?";
    return `${API_BASE}/cameras/${selectedCameraId}/live${queryPrefix}${separator}${cacheBuster}`;
  };

  // Build stream URL with token
  useEffect(() => {
    const token = getAccessToken();

    if (!token) {
      setError("Please login to view camera stream");
      setIsLoading(false);
      return;
    }

    setIsLoading(true);
    setError(null);

    setStreamUrl(buildStreamUrl(token, "remote"));

    // Safety timeout: hide loading after 3 seconds even if no onLoad event
    const timer = setTimeout(() => {
      setIsLoading(false);
    }, 3000);

    return () => clearTimeout(timer);
  }, [API_BASE, selectedCameraId]);

  // Handle camera change
  const handleCameraChange = (e) => {
    const newId = Number(e.target.value);
    setIsLoading(true);
    setError(null);
    setSelectedCameraId(newId);
  };

  // Handle refresh
  const handleRefresh = () => {
    setError(null);
    setIsLoading(true);
    setStreamUrl("");

    const token = getAccessToken();
    if (!token) {
      setError("Please login to view camera stream");
      setIsLoading(false);
      return;
    }

    setStreamUrl(buildStreamUrl(token, "remote"));
  };

  // Handle fullscreen
  const toggleFullscreen = () => {
    if (!containerRef.current) return;
    if (!document.fullscreenElement) {
      containerRef.current.requestFullscreen();
    } else {
      document.exitFullscreen();
    }
  };

  // Loading state for cameras
  if (camerasLoading) {
    return (
      <FadeIn delay={0.15}>
        <Card className="overflow-hidden border-slate-800 bg-slate-900">
          <CardContent className="p-6">
            <div className="flex items-center justify-center h-64">
              <div className="h-8 w-8 animate-spin rounded-full border-4 border-blue-500 border-t-transparent"></div>
              <span className="ml-3 text-slate-400">Loading cameras...</span>
            </div>
          </CardContent>
        </Card>
      </FadeIn>
    );
  }

  return (
    <FadeIn delay={0.15}>
      <Card
        ref={containerRef}
        className="overflow-hidden border-slate-800 bg-slate-900 transition-all duration-300 hover:-translate-y-1 hover:shadow-xl"
      >
        {/* Header */}
        <CardHeader className="flex flex-row items-center justify-between border-b border-slate-800 px-5 py-3">
          <div className="flex items-center gap-3">
            <Camera size={20} className="text-blue-400" />
            <div>
              <CardTitle className="text-lg text-white">Live Camera Feed</CardTitle>
              <div className="flex items-center gap-2 mt-0.5">
                <select
                  id="camera-select"
                  value={selectedCameraId}
                  onChange={handleCameraChange}
                  className="text-xs bg-slate-800 border border-slate-700 rounded-lg px-2 py-1 text-white focus:outline-none focus:border-blue-500"
                >
{cameras?.map((cam) => (
                    <option key={cam.id} value={cam.id}>
                      {cam.name} ({cam.location})
                    </option>
                  ))}
                </select>
              </div>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <LivePulse label="LIVE" />
          </div>
        </CardHeader>

        <CardContent className="p-0">
          {/* Camera Feed */}
          <div className="relative aspect-video min-h-[260px] lg:min-h-[320px] bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
            
            {/* Loading Overlay - Shows only while loading */}
            {isLoading && (
              <div className="absolute inset-0 flex flex-col items-center justify-center z-10 bg-slate-900/80">
                <div className="h-12 w-12 animate-spin rounded-full border-4 border-blue-500 border-t-transparent"></div>
                <p className="mt-4 text-sm text-slate-400">Connecting to camera...</p>
              </div>
            )}

            {/* Error Overlay */}
            {error && !isLoading && (
              <div className="absolute inset-0 flex flex-col items-center justify-center z-10 bg-slate-900/90">
                <Camera size={48} className="text-slate-600 mb-3" />
                <p className="text-sm text-red-400 text-center px-4">{error}</p>
                <button
                  onClick={handleRefresh}
                  className="mt-3 rounded-lg bg-slate-800 px-4 py-2 text-sm text-white hover:bg-slate-700 transition-colors"
                >
                  <RefreshCw className="h-4 w-4 inline mr-2" />
                  Retry
                </button>
              </div>
            )}

            {/* Video Stream - Always rendered, hidden during loading */}
            {streamUrl && (
              <img
                ref={imgRef}
                src={streamUrl}
                alt="Live Camera Feed"
                className="h-full w-full object-contain"
                onLoad={() => {
                  setIsLoading(false);
                  setError(null);
                }}
                onError={() => {
                  const token = getAccessToken();
                  if (streamUrl.includes("localhost:8080/stream") && token) {
                    setIsLoading(true);
                    setStreamUrl("");
                    setTimeout(() => setStreamUrl(buildStreamUrl(token, "backend")), 80);
                    return;
                  }
                  setIsLoading(false);
                  setStreamUrl("");
                  setError("Unable to connect to camera. Please check if camera is online.");
                }}
              />
            )}

            {/* Controls */}
            <div className="absolute left-4 top-4">
              <LivePulse />
            </div>

            <div className="absolute right-4 top-4 flex items-center gap-2">
              <button
                onClick={handleRefresh}
                className="rounded-lg bg-slate-900/80 p-2 text-slate-300 transition hover:bg-slate-700 hover:text-white"
                disabled={isLoading}
              >
                <RefreshCw size={18} className={isLoading ? "animate-spin" : ""} />
              </button>
              <button
                onClick={toggleFullscreen}
                className="rounded-lg bg-slate-900/80 p-2 text-slate-300 transition hover:bg-slate-700 hover:text-white"
              >
                <Maximize2 size={18} />
              </button>
            </div>

          {/* Camera Name Overlay */}
            {selectedCamera && !isLoading && !error && (
              <div className="absolute bottom-4 left-4 bg-slate-900/80 px-3 py-1.5 rounded-lg">
                <span className="text-sm text-white font-medium">{selectedCamera.name}</span>
                <span className="text-xs text-slate-400 ml-2">{selectedCamera.location}</span>
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </FadeIn>
  );
}