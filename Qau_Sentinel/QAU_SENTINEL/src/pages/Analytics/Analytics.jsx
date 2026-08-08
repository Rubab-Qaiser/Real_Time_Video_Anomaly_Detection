import PageHeader from "@/components/layout/PageHeader";
import { PageTransition } from "@/components/animations";

import AnalyticsFilters from "@/components/analytics/AnalyticsFilters";
import AnalyticsOverview from "@/components/analytics/AnalyticsOverview";
import IncidentTrendChart from "@/components/analytics/IncidentTrendChart";
import MonthlyTrendChart from "@/components/analytics/MonthlyTrendChart";
import DetectionDistribution from "@/components/analytics/DetectionDistribution";
import CameraPerformance from "@/components/analytics/CameraPerformance";
import RecentReports from "@/components/analytics/RecentReports";
import ReportActions from "@/components/analytics/ReportActions";

import useAnalytics from "@/hooks/useAnalytics";

import LoadingSpinner from "@/components/common/LoadingSpinner";
import EmptyState from "@/components/common/EmptyState";
import ErrorState from "@/components/common/ErrorState";

export default function Analytics() {
  const {
    analytics,
    loading,
    error,
    refresh,
  } = useAnalytics();

  if (loading) {
    return (
      <LoadingSpinner
        text="Loading analytics..."
        fullScreen
      />
    );
  }

  if (error) {
    return (
      <ErrorState
        title="Analytics unavailable"
        description="Unable to load analytics data."
        onRetry={refresh}
      />
    );
  }

  if (!analytics) {
    return (
      <EmptyState
        title="No analytics data"
        description="Analytics statistics are currently unavailable."
      />
    );
  }

  return (
    <PageTransition>
      <div className="space-y-6">

        <PageHeader
          title="Analytics & Reports"
          subtitle="Monitor AI performance, incident trends, and surveillance statistics."
        />

        <AnalyticsFilters />

        <AnalyticsOverview data={analytics.overview} />

        {/* Trend Charts - Weekly & Monthly */}
        <div className="grid grid-cols-1 gap-6 xl:grid-cols-2">
          <IncidentTrendChart data={analytics.incidentTrend} />
          <MonthlyTrendChart data={analytics.monthlyTrend} />
        </div>

        <DetectionDistribution data={analytics.detectionDistribution} />

        <CameraPerformance data={analytics.cameraPerformance} />

        <ReportActions />

        <RecentReports reports={analytics.reports} />

      </div>
    </PageTransition>
  );
}