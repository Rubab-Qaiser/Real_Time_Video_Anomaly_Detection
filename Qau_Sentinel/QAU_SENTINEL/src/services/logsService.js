import api from "@/api/axios";

const logsService = {
  async getLogs({
    page = 1,
    search = "",
    severity = "All",
  }) {
    const { data } = await api.get("/logs", {
      params: {
        page,
        search,
        severity,
      },
    });

    return data;
  },
};

export default logsService;