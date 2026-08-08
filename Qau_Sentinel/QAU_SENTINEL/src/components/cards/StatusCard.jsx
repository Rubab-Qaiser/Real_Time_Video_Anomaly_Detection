import { Card, CardContent } from "@/components/ui/card";
import {
  AnimatedCounter,
  FadeIn,
} from "@/components/animations";

const variants = {
  blue: {
    icon: "bg-blue-500/15 text-blue-400",
    border: "border-blue-500/20",
  },

  green: {
    icon: "bg-emerald-500/15 text-emerald-400",
    border: "border-emerald-500/20",
  },

  red: {
    icon: "bg-red-500/15 text-red-400",
    border: "border-red-500/20",
  },

  yellow: {
    icon: "bg-yellow-500/15 text-yellow-400",
    border: "border-yellow-500/20",
  },
};

export default function StatusCard({
  title,
  value,
  status,
  icon: Icon,
  color = "blue",
}) {
  const style = variants[color] || variants.blue;

  const isNumber =
    typeof value === "number" ||
    (!isNaN(value) && value !== "");

  return (
    <FadeIn>

      <Card
        className={`
          border
          ${style.border}
          bg-slate-900
          transition-all
          duration-300
          hover:-translate-y-1
          hover:border-slate-600
          hover:shadow-lg
        `}
      >

        <CardContent className="p-4">

          <div className="flex items-start justify-between">

            <div>

              <p className="text-xs uppercase tracking-wide text-slate-400">
                {title}
              </p>

              <h2 className="mt-2 text-2xl font-bold text-white lg:text-3xl">

                {isNumber ? (
                  <AnimatedCounter value={Number(value)} />
                ) : (
                  value
                )}

              </h2>

              <p className="mt-2 text-xs text-slate-500">
                {status}
              </p>

            </div>

            <div
              className={`
                flex
                h-12
                w-12
                items-center
                justify-center
                rounded-xl
                ${style.icon}
              `}
            >
              <Icon size={22} />
            </div>

          </div>

        </CardContent>

      </Card>

    </FadeIn>
  );
}