import {
  Camera,
  Cpu,
  Brain,
  ShieldCheck,
  CheckCircle2,
  ChevronRight,
} from "lucide-react";

export default function SystemActivityCard({ incidents = [] }) {
  const activities = [
    {
      id: 1,
      title: "Camera Stream",
      description: incidents[0]?.camera || "Live camera feed connected",
      time: "Just now",
      icon: Camera,
    },
    {
      id: 2,
      title: "AI Detection Engine",
      description: "Live models are processing incoming frames",
      time: "Live",
      icon: Cpu,
    },
    {
      id: 3,
      title: "Latest Event",
      description: incidents[0]
        ? `${incidents[0].type || incidents[0].detection_type} detected on ${incidents[0].camera || "camera"}`
        : "No event received yet",
      time: incidents[0]?.timestamp
        ? new Date(incidents[0].timestamp).toLocaleTimeString([], {
            hour: "2-digit",
            minute: "2-digit",
          })
        : "Waiting",
      icon: Brain,
    },
    {
      id: 4,
      title: "Monitoring Active",
      description: "Continuous surveillance running in real time",
      time: "Live",
      icon: ShieldCheck,
    },
  ];

  return (
    <div className="rounded-2xl border border-slate-800 bg-[#111827] shadow-lg">

      {/* ==========================================
          Header
      ========================================== */}

      <div className="flex items-center justify-between border-b border-slate-800 px-5 py-4">

        <div>
          <h2 className="text-lg font-semibold text-white">
            System Activity
          </h2>

          <p className="mt-1 text-sm text-slate-400">
            Latest operational events
          </p>
        </div>

        <button
          className="
            flex
            items-center
            gap-1
            text-sm
            text-blue-400
            transition
            hover:text-blue-300
          "
        >
          View All
          <ChevronRight size={16} />
        </button>

      </div>

      {/* ==========================================
          Activity Feed
      ========================================== */}

      <div className="divide-y divide-slate-800">

        {activities.map((activity) => {
          const Icon = activity.icon;

          return (
            <div
              key={activity.id}
              className="
                flex
                items-center
                justify-between
                px-5
                py-4
                transition
                hover:bg-slate-800/40
              "
            >
              {/* Left */}

              <div className="flex items-center gap-4">

                <div className="rounded-xl bg-green-500/10 p-3">
                  <Icon
                    size={20}
                    className="text-green-400"
                  />
                </div>

                <div>

                  <h3 className="font-medium text-white">
                    {activity.title}
                  </h3>

                  <p className="mt-1 text-sm text-slate-400">
                    {activity.description}
                  </p>

                </div>

              </div>

              {/* Right */}

              <div className="text-right">

                <div className="flex items-center justify-end gap-2">

                  <CheckCircle2
                    size={16}
                    className="text-green-400"
                  />

                  <span className="text-sm font-semibold text-green-400">
                    OK
                  </span>

                </div>

                <p className="mt-2 text-xs text-slate-500">
                  {activity.time}
                </p>

              </div>

            </div>
          );
        })}

      </div>

    </div>
  );
}