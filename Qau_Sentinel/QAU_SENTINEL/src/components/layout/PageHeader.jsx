import { FadeIn } from "@/components/animations";

export default function PageHeader({
  title,
  subtitle,
  action,
}) {
  return (
    <FadeIn>

      <div
        className="
          mb-4
          flex
          flex-col
          gap-3
          md:flex-row
          md:items-center
          md:justify-between
        "
      >

        {/* Left */}

        <div>

          <h1
            className="
              text-3xl
              font-bold
              tracking-tight
              text-white
            "
          >
            {title}
          </h1>

          {subtitle && (

            <p
              className="
                mt-1
                max-w-3xl
                text-sm
                text-slate-400
              "
            >
              {subtitle}
            </p>

          )}

        </div>

        {/* Right */}

        {action && (
          <div className="flex items-center">
            {action}
          </div>
        )}

      </div>

    </FadeIn>
  );
}