import { lazy, Suspense } from "react";
import { Routes, Route } from "react-router-dom";

import DashboardLayout from "@/layouts/DashboardLayout";
import AuthLayout from "@/layouts/AuthLayout";
import ProtectedRoute from "@/components/auth/ProtectedRoute";

import { PageTransition } from "@/components/animations";
import LoadingSpinner from "@/components/common/LoadingSpinner";

const Dashboard = lazy(() => import("@/pages/Dashboard/Dashboard"));
const Cameras = lazy(() => import("@/pages/Cameras/Cameras"));
const Incidents = lazy(() => import("@/pages/Incidents/Incidents"));
const Analytics = lazy(() => import("@/pages/Analytics/Analytics"));
const Logs = lazy(() => import("@/pages/Logs/Logs"));
const Users = lazy(() => import("@/pages/Users/Users"));
const Settings = lazy(() => import("@/pages/Settings/Settings"));
const Login = lazy(() => import("@/pages/Login/Login"));

const withTransition = (Component) => (
  <PageTransition>
    <Suspense fallback={<LoadingSpinner text="Opening page..." fullScreen />}>
      <Component />
    </Suspense>
  </PageTransition>
);

export default function AppRoutes() {
  return (
    <Routes>

      {/* ============= AUTHENTICATION ============= */}

      <Route element={<AuthLayout />}>
        <Route
          path="/login"
          element={withTransition(Login)}
        />
      </Route>

      {/* ============= PROTECTED ROUTES ============= */}

      <Route element={<ProtectedRoute />}>
        <Route element={<DashboardLayout />}>

          <Route
            path="/"
            element={withTransition(Dashboard)}
          />

          <Route
            path="/cameras"
            element={withTransition(Cameras)}
          />

          <Route
            path="/incidents"
            element={withTransition(Incidents)}
          />

          <Route
            path="/analytics"
            element={withTransition(Analytics)}
          />

          <Route
            path="/logs"
            element={withTransition(Logs)}
          />

          <Route
            path="/settings"
            element={withTransition(Settings)}
          />

        </Route>
      </Route>

      {/* ============= ADMIN ONLY ROUTES ============= */}

      <Route element={<ProtectedRoute requiredRoles={["Admin"]} />}>
        <Route element={<DashboardLayout />}>

          <Route
            path="/users"
            element={withTransition(Users)}
          />

        </Route>
      </Route>

    </Routes>
  );
}
