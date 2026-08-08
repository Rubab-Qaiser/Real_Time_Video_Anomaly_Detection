import { useCallback, useEffect, useState } from "react";

import analyticsService from "@/services/analyticsService";

export default function useAnalytics() {
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchAnalytics = useCallback(async () => {
    try {
      setError(null);

      const response = await analyticsService.getOverview();

      setAnalytics({
        overview: {
          totalIncidents: response.dashboard?.total_incidents ?? 0,
          activeCameras: response.dashboard?.total_cameras ?? 0,
          averageConfidence: response.dashboard?.average_confidence ?? 0,
          aiAccuracy: response.dashboard?.ai_accuracy ?? 0,
        },

        incidentTrend: response.trends?.weekly ?? [],
        monthlyTrend: response.trends?.monthly ?? [],

        detectionDistribution: Object.entries(
          response.distribution ?? {}
        ).map(([name, value]) => ({
          name,
          value: Number(value) || 0,
        })),

        cameraPerformance: response.camera_performance ?? [],

        reports: response.reports ?? [],
      });
    } catch (err) {
      console.error("Failed to fetch analytics:", err);
      setError(err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchAnalytics();
    const intervalId = window.setInterval(fetchAnalytics, 5000);
    return () => window.clearInterval(intervalId);
  }, [fetchAnalytics]);

  return {
    analytics,
    loading,
    error,
    refresh: fetchAnalytics,
  };
}