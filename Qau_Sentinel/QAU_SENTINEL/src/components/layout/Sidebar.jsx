import { NavLink } from "react-router-dom";
import { ChevronRight } from "lucide-react";

import { navigation } from "@/utils/navigation";
import logo from "@/assets/logo/qau_logo.jpeg";

export default function Sidebar() {
  return (
    <aside className="flex h-full flex-col bg-[#111827] text-white">

      {/* ===========================
          Branding
      =========================== */}

      <div className="border-b border-slate-800 px-6 py-7">

        <div className="flex items-center gap-4">

          <div className="flex h-14 w-14 items-center justify-center rounded-xl bg-white p-2 shadow-md">

            <img
              src={logo}
              alt="QAU Logo"
              className="h-full w-full object-contain"
            />

          </div>

          <div>

            <h1 className="text-lg font-bold tracking-wide">
              QAU Sentinel
            </h1>

            <p className="mt-1 text-xs leading-5 text-slate-400">
              AI Safety &
              <br />
              Anomaly Detection Platform
            </p>

          </div>

        </div>

      </div>

      {/* ===========================
          Navigation
      =========================== */}

      <div className="flex-1 overflow-y-auto px-4 py-6">

        {navigation.map((section) => (

          <div
            key={section.group}
            className="mb-8"
          >

            <h3 className="mb-3 px-3 text-[11px] font-semibold uppercase tracking-[0.18em] text-slate-500">

              {section.group}

            </h3>

            <div className="space-y-2">

              {section.items.map((item) => {

                const Icon = item.icon;

                return (

                  <NavLink
                    key={item.path}
                    to={item.path}
                    className={({ isActive }) =>
                      `group flex items-center justify-between rounded-xl px-4 py-3 transition-all duration-200 ${
                        isActive
                          ? "border-l-4 border-blue-500 bg-blue-600/20 text-blue-400 shadow-md"
                          : "text-slate-300 hover:bg-slate-800 hover:text-white"
                      }`
                    }
                  >
                    <div className="flex items-center gap-3">

                      <Icon
                        size={20}
                        className="transition-transform duration-200 group-hover:scale-110"
                      />

                      <span className="font-medium">
                        {item.title}
                      </span>

                    </div>

                    <ChevronRight
                      size={16}
                      className="opacity-0 transition-all duration-200 group-hover:translate-x-1 group-hover:opacity-100"
                    />

                  </NavLink>

                );

              })}

            </div>

          </div>

        ))}

      </div>

      {/* ===========================
          Footer
      =========================== */}

      <div className="border-t border-slate-800 px-6 py-5">

        <p className="text-xs font-medium text-slate-400">
          QAU Sentinel
        </p>

        <p className="mt-1 text-xs text-slate-500">
          Version 1.0.0
        </p>

      </div>

    </aside>
  );
}