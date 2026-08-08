import { useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  Bell,
  Bot,
  Search,
  UserCircle2,
  LogOut,
  Settings,
  User,
} from "lucide-react";

import { useAuth } from "@/contexts/AuthContext";
import useClock from "@/hooks/useClock";
import { Input } from "@/components/ui/input";
import SocketStatus from "@/components/common/SocketStatus";

export default function Navbar() {
  const { date, time } = useClock();
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [showDropdown, setShowDropdown] = useState(false);

  const handleLogout = async () => {
    await logout();
    navigate("/login");
  };

  // Role badge color
  const roleColors = {
    Admin: "bg-purple-600/20 text-purple-400 border-purple-600/30",
    Operator: "bg-blue-600/20 text-blue-400 border-blue-600/30",
    Viewer: "bg-slate-600/20 text-slate-400 border-slate-600/30",
  };

  return (
    <nav className="flex h-16 items-center justify-between px-4 lg:px-6">
      {/* Left */}
      <div className="flex items-center gap-4">
        <div className="relative hidden md:block">
          <Search
            size={18}
            className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400"
          />
          <Input
            placeholder="Search..."
            className="
              h-10
              w-56
              border-slate-700
              bg-slate-900
              pl-10
              text-sm
              text-white
              placeholder:text-slate-500
              lg:w-72
            "
          />
        </div>
      </div>

      {/* Right */}
      <div className="flex items-center gap-5">
        {/* Socket Status */}
        <div className="hidden lg:flex">
          <SocketStatus />
        </div>

        {/* Date & Time */}
        <div className="hidden text-right xl:block">
          <p className="text-xs text-slate-400">{date}</p>
          <p className="font-semibold text-white">{time}</p>
        </div>

        {/* Notifications */}
        <button className="rounded-xl p-2.5 text-slate-400 transition-all duration-200 hover:bg-slate-800 hover:text-white">
          <Bell size={20} />
        </button>

        {/* AI */}
        <button className="rounded-xl p-2.5 text-blue-400 transition-all duration-200 hover:bg-slate-800">
          <Bot size={20} />
        </button>

        {/* User Profile */}
        <div className="relative">
          <button
            onClick={() => setShowDropdown(!showDropdown)}
            className="
              flex
              items-center
              gap-2
              rounded-xl
              border
              border-slate-800
              bg-slate-900
              px-3
              py-2
              transition-all
              duration-200
              hover:border-slate-700
              group
            "
          >
            <UserCircle2
              size={28}
              className="text-slate-300 group-hover:text-blue-400 transition-colors duration-200"
            />

            <div className="hidden text-left lg:block">
              <p className="text-sm font-medium text-white">
                {user?.username || "User"}
              </p>

              <div className="flex items-center gap-1.5">
                <span
                  className={`text-xs rounded-full px-2 py-0.5 border ${
                    roleColors[user?.role] || roleColors.Viewer
                  }`}
                >
                  {user?.role || "Viewer"}
                </span>
              </div>
            </div>
          </button>

          {/* Dropdown */}
          {showDropdown && (
            <>
              <div
                className="fixed inset-0 z-10"
                onClick={() => setShowDropdown(false)}
              />

              <div className="absolute right-0 top-full mt-2 z-20 w-56 rounded-xl border border-slate-800 bg-slate-900 py-1 shadow-xl">
                <div className="border-b border-slate-800 px-4 py-3">
                  <p className="text-sm font-medium text-white">
                    {user?.username}
                  </p>
                  <p className="text-xs text-slate-400 truncate">
                    {user?.email}
                  </p>
                </div>

                <button
                  onClick={() => {
                    setShowDropdown(false);
                    navigate("/settings");
                  }}
                  className="flex w-full items-center gap-3 px-4 py-2.5 text-sm text-slate-300 hover:bg-slate-800 transition-colors"
                >
                  <Settings size={16} />
                  Settings
                </button>

                <button
                  onClick={() => {
                    setShowDropdown(false);
                    navigate("/users");
                  }}
                  className="flex w-full items-center gap-3 px-4 py-2.5 text-sm text-slate-300 hover:bg-slate-800 transition-colors"
                >
                  <User size={16} />
                  Manage Users
                </button>

                <div className="border-t border-slate-800 mt-1 pt-1">
                  <button
                    onClick={handleLogout}
                    className="flex w-full items-center gap-3 px-4 py-2.5 text-sm text-red-400 hover:bg-red-600/20 transition-colors"
                  >
                    <LogOut size={16} />
                    Logout
                  </button>
                </div>
              </div>
            </>
          )}
        </div>
      </div>
    </nav>
  );
}