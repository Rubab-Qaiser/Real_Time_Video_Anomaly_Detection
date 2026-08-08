import { Outlet } from "react-router-dom";

import Sidebar from "@/components/layout/Sidebar";
import Navbar from "@/components/layout/Navbar";

export default function DashboardLayout() {
  return (
    <div className="flex h-screen overflow-hidden bg-slate-950 text-slate-100">

      {/* ==========================================
          Sidebar
      ========================================== */}

      <aside
        className="
          hidden
          lg:flex
          lg:w-72
          xl:w-72
          2xl:w-80
          flex-shrink-0
          border-r
          border-slate-800
          bg-slate-900
        "
      >
        <Sidebar />
      </aside>

      {/* ==========================================
          Main Content
      ========================================== */}

      <div className="flex min-w-0 flex-1 flex-col">

        {/* Navbar */}

        <header
          className="
            sticky
            top-0
            z-40
            border-b
            border-slate-800
            bg-slate-950/95
            backdrop-blur-md
          "
        >
          <Navbar />
        </header>

        {/* Main */}

        <main
          className="
            flex-1
            overflow-y-auto
            px-4
            py-4
            sm:px-5
            lg:px-6
            xl:px-8
          "
        >
          <div
            className="
              mx-auto
              w-full
              max-w-[1700px]
            "
          >
            <Outlet />
          </div>
        </main>

      </div>

    </div>
  );
}