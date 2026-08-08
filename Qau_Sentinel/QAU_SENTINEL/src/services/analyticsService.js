import api from "@/api/axios";

const analyticsService = {
  async getOverview() {
    const { data } = await api.get(
      "/analytics/overview"
    );

    return data;
  },

  async getDashboardStats() {
    const { data } = await api.get(
      "/analytics/dashboard"
    );

    return data;
  },

  async getTrends() {
    const { data } = await api.get(
      "/analytics/trends"
    );

    return data;
  },

  async getDistribution() {
    const { data } = await api.get(
      "/analytics/distribution"
    );

    return data;
  },

  async getCameraPerformance() {
    const { data } = await api.get(
      "/analytics/camera-performance"
    );

    return data;
  },

  async getReports() {
    const { data } = await api.get(
      "/analytics/reports"
    );

    return data;
  },
};

export default analyticsService;