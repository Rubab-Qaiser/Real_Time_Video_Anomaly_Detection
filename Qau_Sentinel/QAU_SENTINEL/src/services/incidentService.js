import api from "@/api/axios";

const incidentService = {
  async getAll(params = {}) {
    const { data } = await api.get(
      "/incidents",
      {
        params,
      }
    );

    return data;
  },

  async getById(id) {
    const { data } = await api.get(
      `/incidents/${id}`
    );

    return data;
  },

  async create(payload) {
    const { data } = await api.post(
      "/incidents",
      payload
    );

    return data;
  },

  async update(id, payload) {
    const { data } = await api.put(
      `/incidents/${id}`,
      payload
    );

    return data;
  },

  async remove(id) {
    const { data } = await api.delete(
      `/incidents/${id}`
    );

    return data;
  },
};

export default incidentService;