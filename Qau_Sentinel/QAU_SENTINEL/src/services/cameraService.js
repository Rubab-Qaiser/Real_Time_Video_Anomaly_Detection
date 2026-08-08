import api from "@/api/axios";

const cameraService = {
  // ============= GET ALL =============
  async getAll(params = {}) {
    const { data } = await api.get("/cameras", { params });
    return data;
  },

  // ============= GET ONE =============
  async getById(id) {
    const { data } = await api.get(`/cameras/${id}`);
    return data;
  },

  // ============= CREATE =============
  async create(cameraData) {
    const { data } = await api.post("/cameras", cameraData);
    return data;
  },

  // ============= UPDATE =============
  async update(id, cameraData) {
    const { data } = await api.put(`/cameras/${id}`, cameraData);
    return data;
  },

  // ============= DELETE =============
  async delete(id) {
    await api.delete(`/cameras/${id}`);
  },

  // ============= STREAM URL =============
  async getStreamUrl(id) {
    const remoteStreamUrl = import.meta.env.VITE_REMOTE_STREAM_URL || "http://localhost:8080/stream";
    const baseUrl = remoteStreamUrl || `${api.defaults.baseURL}/cameras/${id}/stream`;
    const token = localStorage.getItem("qau_access_token");
    const suffix = token ? `${baseUrl.includes("?") ? "&" : "?"}token=${encodeURIComponent(token)}` : "";
    return `${baseUrl}${suffix}`;
  },
};

export default cameraService;