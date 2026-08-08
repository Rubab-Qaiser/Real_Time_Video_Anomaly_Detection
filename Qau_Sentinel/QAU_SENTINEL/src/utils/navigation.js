import {
  LayoutDashboard,
  Camera,
  TriangleAlert,
  ClipboardList,
  BarChart3,
  Users,
  Settings,
} from "lucide-react";

export const navigation = [
  {
    group: "MAIN",
    items: [
      {
        title: "Dashboard",
        path: "/",
        icon: LayoutDashboard,
      },
      {
        title: "Cameras",
        path: "/cameras",
        icon: Camera,
      },
      {
        title: "Incidents",
        path: "/incidents",
        icon: TriangleAlert,
      },
      {
        title: "Logs",
        path: "/logs",
        icon: ClipboardList,
      },
      {
        title: "Analytics",
        path: "/analytics",
        icon: BarChart3,
      },
    ],
  },

  {
    group: "MANAGEMENT",
    items: [
      {
        title: "Users",
        path: "/users",
        icon: Users,
      },
      {
        title: "Settings",
        path: "/settings",
        icon: Settings,
      },
    ],
  },
];