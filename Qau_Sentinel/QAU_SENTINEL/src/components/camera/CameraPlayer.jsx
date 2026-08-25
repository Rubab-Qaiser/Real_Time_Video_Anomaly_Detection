import { useState, useEffect } from "react";
import {
  Camera,
  Expand,
  Maximize2,
} from "lucide-react";

import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

import {
  FadeIn,
  LivePulse,
} from "@/components/animations";

import DetectionOverlay from "@/components/detection/DetectionOverlay";
import DetectionLegend from "@/components/detection/DetectionLegend";
import api from "@/api/axios";

/**
 * Convert a backend detection (e.g. {"class":"Fire","confidence":0.94})
 * into the shape expected by DetectionOverlay / DetectionBox.
 */
function toOverlayShape(detection, index) {
  const label = detection.class || "Unknown";
  const raw = Number(detection.confidence || 0);
  const conf = raw <= 1 ? Math.round(raw * 100) : Math.round(raw);

  const colorMap = {
    Fire: "red",
    Smoke: "yellow",
    Crowd: "blue",
  };

  return {
    id: index,
    label,
    confidence: conf,
    color: colorMap[label] || "red",
    x: 10,
    y: 10 + index * 12,
    width: 20,
    height: 10,
  };
}

export default function CameraPlayer({
  camera = {
    id: 1,
    name: "Main Entrance",
    location: "Gate A",
    status: "online",
    streamUrl: "",
  },
}) {
  const [liveDetections, setLiveDetections] = useState([]);

  // Poll live detections endpoint
  useEffect(() => {
    let isMounted = true;
    const interval = setInterval(async () => {
      try {
        const { data } = await api.get("/detections/");
        if (isMounted && data.detections) {
          setLiveDetections(
            data.detections.map((d, i) => toOverlayShape(d, i))
          );
        }
      } catch {
        // Keep existing detections on error
      }
    }, 2500);

    return () => {
      isMounted = false;
      clearInterval(interval);
    };
  }, []);

  return (
    <FadeIn>

      <Card className="overflow-hidden border-slate-800 bg-slate-900">

        {/* ======================================
            Header
        ====================================== */}

        <div className="flex items-center justify-between border-b border-slate-800 px-5 py-3">

          <div>

            <h2 className="text-lg font-semibold text-white">
              {camera.name}
            </h2>

            <p className="text-sm text-slate-400">
              {camera.location}
            </p>

          </div>

          <LivePulse label="LIVE" />

        </div>

        {/* ======================================
            Video Player
        ====================================== */}

        <div
          className="
            relative
            aspect-video
            overflow-hidden
            bg-gradient-to-br
            from-slate-900
            via-slate-800
            to-slate-900
          "
        >

          {/* ======================================
              Camera Stream
          ====================================== */}

          {camera.streamUrl ? (

            <img
              src={camera.streamUrl}
              alt={camera.name}
              className="h-full w-full object-cover"
            />

          ) : (

            <div className="absolute inset-0 flex flex-col items-center justify-center">

              <Camera
                size={80}
                className="mb-4 text-slate-600"
              />

              <h3 className="text-lg font-semibold text-white">
                Camera Stream
              </h3>

              <p className="mt-1 text-sm text-slate-400">
                Waiting for Flask backend...
              </p>

            </div>

          )}

          {/* ======================================
              YOLO Detection Overlay — live from backend
          ====================================== */}

          <DetectionOverlay
            detections={liveDetections}
          />

          {/* ======================================
              Detection Legend
          ====================================== */}

          <DetectionLegend />

          {/* ======================================
              Live Indicator
          ====================================== */}

          <div className="absolute left-4 top-4 z-30">
            <LivePulse label="LIVE" />
          </div>

          {/* ======================================
              Expand Buttons
          ====================================== */}

          <Button
            size="icon"
            variant="secondary"
            className="
              absolute
              right-4
              top-4
              z-30
              bg-slate-900/80
              hover:bg-slate-700
            "
          >
            <Expand size={18} />
          </Button>

          <Button
            size="icon"
            variant="secondary"
            className="
              absolute
              bottom-4
              right-4
              z-30
              bg-slate-900/80
              hover:bg-slate-700
            "
          >
            <Maximize2 size={18} />
          </Button>

        </div>

      </Card>

    </FadeIn>
  );
}
