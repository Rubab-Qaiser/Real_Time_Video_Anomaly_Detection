import {
  useEffect,
  useState,
} from "react";
import {
  Flame,
  CloudFog,
  Users,
  Camera,
  Cpu,
  Clock3,
  CheckCircle2,
} from "lucide-react";

import api from "@/api/axios";

export default function DetectionStatusCard() {
  const [liveStatus, setLiveStatus] = useState({
    fire: false,
    smoke: false,
    crowd: false,
    areaM2: null,
    densityPeoplePerM2: null,
    zoneDensities: [],
    headPositionsWorld: [],
    events: [],
  });

  useEffect(() => {
    let isMounted = true;

    const fetchLatestStatus = async () => {
      try {
        const { data } = await api.get("/detections/latest");
        if (isMounted) {
          setLiveStatus({
            fire: Boolean(data.fire),
            smoke: Boolean(data.smoke),
            crowd: Boolean(data.crowd),
            areaM2: data.area_m2 ?? null,
            densityPeoplePerM2: data.density_people_per_m2 ?? null,
            zoneDensities: data.zone_densities || [],
            headPositionsWorld: data.head_positions_world || [],
            events: data.events || [],
          });
        }
      } catch (error) {
        console.error("Failed to fetch live detection status:", error);
      }
    };

    fetchLatestStatus();
    const intervalId = window.setInterval(fetchLatestStatus, 2500);

    return () => {
      isMounted = false;
      window.clearInterval(intervalId);
    };
  }, []);

  const detectionItems = [
    {
      title: "Fire",
      value: liveStatus.fire ? "DETECTED" : "SAFE",
      icon: Flame,
      color: liveStatus.fire ? "text-red-400" : "text-green-400",
      bg: liveStatus.fire ? "bg-red-500/10" : "bg-green-500/10",
    },
    {
      title: "Smoke / Haze",
      value: liveStatus.smoke ? "DETECTED" : "CLEAR",
      icon: CloudFog,
      color: liveStatus.smoke ? "text-yellow-400" : "text-green-400",
      bg: liveStatus.smoke ? "bg-yellow-500/10" : "bg-green-500/10",
    },
    {
      title: "Crowd Density",
      value: liveStatus.densityPeoplePerM2 != null
        ? `${liveStatus.densityPeoplePerM2.toFixed(2)} p/m²`
        : (liveStatus.crowd ? "HIGH" : "NORMAL"),
      icon: Users,
      color: liveStatus.crowd ? "text-orange-400" : "text-blue-400",
      bg: liveStatus.crowd ? "bg-orange-500/10" : "bg-blue-500/10",
    },
  ];

  // Compute zone-density detail string for the Crowd row's subtitle
  const crowdDetail = (() => {
    if (liveStatus.zoneDensities.length > 0) {
      return liveStatus.zoneDensities
        .map((z) => `${z.zone_name || "zone"}: ${z.density_people_per_m2?.toFixed(2) ?? z.density_people_per_m2 ?? 0} p/m²`)
        .join(", ");
    }
    if (liveStatus.areaM2 != null) {
      return `Area: ${liveStatus.areaM2.toFixed(1)} m²`;
    }
    return "Current Status";
  })();

  return (
    <div className="rounded-2xl border border-slate-800 bg-[#111827] shadow-lg">

      {/* Header */}

      <div className="border-b border-slate-800 px-5 py-4">
        <h2 className="text-lg font-semibold text-white">
          AI Detection Status
        </h2>

        <p className="mt-1 text-sm text-slate-400">
          Live anomaly analysis
        </p>
      </div>

      {/* Detection Results */}

      <div className="space-y-3 p-5">

        {detectionItems.map((item) => {
          const Icon = item.icon;

          return (
            <div
              key={item.title}
              className="
                flex
                items-center
                justify-between
                rounded-xl
                border
                border-slate-800
                bg-slate-900/60
                px-4
                py-3
              "
            >
              <div className="flex items-center gap-3">

                <div className={`${item.bg} rounded-lg p-2.5`}>
                  <Icon
                    size={18}
                    className={item.color}
                  />
                </div>

                <div>

                  <p className="text-sm font-medium text-white">
                    {item.title}
                  </p>

<p className="text-xs text-slate-500">
                    {item.title === "Crowd Density" ? crowdDetail : "Current Status"}
                  </p>

                </div>

              </div>

              <div className="flex items-center gap-2">

                <CheckCircle2
                  size={18}
                  className={item.color}
                />

                <span
                  className={`text-sm font-semibold ${item.color}`}
                >
                  {item.value}
                </span>

              </div>

            </div>
          );
        })}

      </div>

      {/* Divider */}

      <div className="border-t border-slate-800" />

      {/* System Information */}

      <div className="space-y-3 p-5">

        <div className="flex items-center justify-between">

          <div className="flex items-center gap-2">

            <Camera
              size={16}
              className="text-slate-400"
            />

            <span className="text-sm text-slate-400">
              Camera
            </span>

          </div>

          <span className="text-sm font-semibold text-green-400">
            Connected
          </span>

        </div>

        <div className="flex items-center justify-between">

          <div className="flex items-center gap-2">

            <Cpu
              size={16}
              className="text-slate-400"
            />

            <span className="text-sm text-slate-400">
              AI Engine
            </span>

          </div>

          <span className="text-sm font-semibold text-green-400">
            Online
          </span>

        </div>

        <div className="flex items-center justify-between">

          <div className="flex items-center gap-2">

            <Clock3
              size={16}
              className="text-slate-400"
            />

            <span className="text-sm text-slate-400">
              Last Scan
            </span>

          </div>

          <span className="text-sm font-semibold text-white">
            Just Now
          </span>

        </div>

      </div>
    </div>
  );
}