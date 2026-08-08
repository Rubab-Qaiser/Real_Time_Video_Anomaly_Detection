import {
  Camera,
  Flame,
  Users,
  Footprints,
  Activity,
  Swords,
  Package,
} from "lucide-react";

import { FadeIn } from "@/components/animations";

import PageHeader from "@/components/layout/PageHeader";

import StatusCard from "@/components/cards/StatusCard";
import LiveCameraCard from "@/components/cards/LiveCameraCard";
import DetectionStatusCard from "@/components/cards/DetectionStatusCard";
import RecentIncidentsCard from "@/components/cards/RecentIncidentsCard";
import SystemActivityCard from "@/components/cards/SystemActivityCard";
import AnalyticsOverview from "@/components/analytics/AnalyticsOverview";

import useAnalytics from "@/hooks/useAnalytics";
import useIncidents from "@/hooks/useIncidents";  // ✅ Add this

import LoadingSpinner from "@/components/common/LoadingSpinner";
import EmptyState from "@/components/common/EmptyState";
import ErrorState from "@/components/common/ErrorState";

// ✅ Import IncidentStats
import IncidentStats from "@/components/incidents/IncidentStats";

export default function Dashboard() {
  const {
    analytics,
    loading: analyticsLoading,
    error: analyticsError,
    refresh: refreshAnalytics,
  } = useAnalytics();

  // ✅ Fetch incidents for stats
  const {
    incidents,
    loading: incidentsLoading,
    error: incidentsError,
    refresh: refreshIncidents,
  } = useIncidents();

  if (analyticsLoading || incidentsLoading) {
    return (
      <LoadingSpinner
        text="Loading dashboard..."
        fullScreen
      />
    );
  }

  if (analyticsError || incidentsError) {
    return (
      <ErrorState
        title="Dashboard unavailable"
        description="Unable to load dashboard data."
        onRetry={() => {
          refreshAnalytics();
          refreshIncidents();
        }}
      />
    );
  }

  if (!analytics) {
    return (
      <EmptyState
        title="No dashboard data"
        description="Dashboard statistics are currently unavailable."
      />
    );
  }

  return (
    <div className="flex flex-col gap-4">
      {/* ==========================================
          Page Header
      ========================================== */}

      <PageHeader
        title="Command Center"
        subtitle="Real-time AI monitoring for Fire, Smoke/Haze and Crowd Density Detection."
      />

      {/* Analytics Overview */}
      <AnalyticsOverview data={analytics.overview} />

      {/* ==========================================
          Incident Stats - Using the updated component
      ========================================== */}

      <IncidentStats incidents={incidents} />

      {/* ==========================================
          Live Camera + Detection Status
      ========================================== */}

      <section className="grid grid-cols-1 gap-4 xl:grid-cols-12">
        <div className="xl:col-span-8">
          <LiveCameraCard />
        </div>

        <div className="xl:col-span-4">
          <FadeIn delay={0.2}>
            <DetectionStatusCard />
          </FadeIn>
        </div>
      </section>

      {/* ==========================================
          Bottom Section
      ========================================== */}

      <section className="grid grid-cols-1 gap-4 xl:grid-cols-2">
        <FadeIn delay={0.3}>
          <RecentIncidentsCard incidents={incidents.slice(0, 5)} />
        </FadeIn>

        <FadeIn delay={0.4}>
          <SystemActivityCard incidents={incidents.slice(0, 5)} />
        </FadeIn>
      </section>
    </div>
  );
}