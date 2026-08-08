import api from "@/api/axios";

const authService = {
  /**
   * Login user with email and password
   */
  async login(email, password) {
    const { data } = await api.post("/auth/login", { email, password });
    return data;
  },

  /**
   * Refresh access token using refresh token
   */
  async refreshToken(refreshToken) {
    const { data } = await api.post("/auth/refresh", { refresh_token: refreshToken });
    return data;
  },

  /**
   * Logout user
   */
  async logout(refreshToken) {
    await api.post("/auth/logout", { refresh_token: refreshToken });
  },

  /**
   * Get current user from API
   */
  async getCurrentUser() {
    const { data } = await api.get("/auth/me");
    return data;
  },
};

export default authService;