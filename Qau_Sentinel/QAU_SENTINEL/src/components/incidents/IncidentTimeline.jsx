import {
  Clock,
  Camera,
  Bot,
  ShieldAlert,
  CheckCircle2,
} from "lucide-react";

const EVENTS = [
  {
    id: 1,
    icon: Camera,
    title: "Camera captured activity",
    description: "Motion detected by the surveillance camera.",
    time: "10:31:20",
  },
  {
    id: 2,
    icon: Bot,
    title: "AI detection completed",
    description: "YOLO identified the object with high confidence.",
    time: "10:31:22",
  },
  {
    id: 3,
    icon: ShieldAlert,
    title: "Incident created",
    description: "Alert generated and added to the incident queue.",
    time: "10:31:24",
  },
  {
    id: 4,
    icon: CheckCircle2,
    title: "Awaiting operator review",
    description: "Security staff can now review this incident.",
    time: "Pending",
  },
];

export default function IncidentTimeline() {
  return (
    <div>

      <h3 className="mb-4 text-lg font-semibold text-white">
        Timeline
      </h3>

      <div className="space-y-5">

        {EVENTS.map((event) => {
          const Icon = event.icon;

          return (
            <div
              key={event.id}
              className="flex gap-4"
            >
              <div className="flex h-10 w-10 items-center justify-center rounded-full bg-slate-800">
                <Icon
                  size={18}
                  className="text-blue-400"
                />
              </div>

              <div className="flex-1">

                <div className="flex items-center justify-between">

                  <h4 className="font-medium text-white">
                    {event.title}
                  </h4>

                  <span className="flex items-center gap-1 text-xs text-slate-500">
                    <Clock size={12} />
                    {event.time}
                  </span>

                </div>

                <p className="mt-1 text-sm text-slate-400">
                  {event.description}
                </p>

              </div>

            </div>
          );
        })}

      </div>

    </div>
  );
}