import api from "@/api/axios";

const userService = {
  async getAll(params = {}) {
    const { data } = await api.get("/users", { params });
    return data;
  },

  async getById(id) {
    const { data } = await api.get(`/users/${id}`);
    return data;
  },

  async create(userData) {
    const { data } = await api.post("/users", userData);
    return data;
  },

  async update(id, userData) {
    const { data } = await api.put(`/users/${id}`, userData);
    return data;
  },

  async delete(id) {
    await api.delete(`/users/${id}`);
  },
};

export default userService;