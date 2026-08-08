import axios from "axios";
import {
  getAccessToken,
  getRefreshToken,
  setTokens,
  clearAuth,
} from "@/utils/token";
import authService from "@/services/authService";

// ✅ Use the environment variable
const BASE_URL =
  import.meta.env.VITE_API_URL || "http://localhost:5000/api";

const api = axios.create({
  baseURL: BASE_URL,
  timeout: 60000,
  headers: {
    "Content-Type": "application/json",
  },
  // ❌ REMOVE this line - it causes CORS conflict with wildcard
  // withCredentials: true,
});

// ============= REQUEST INTERCEPTOR =============
api.interceptors.request.use(
  (config) => {
    const token = getAccessToken();

    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    return config;
  },
  (error) => Promise.reject(error)
);

// ============= RESPONSE INTERCEPTOR =============
let isRefreshing = false;
let refreshSubscribers = [];

function onRefreshed(token) {
  refreshSubscribers.forEach((callback) => callback(token));
  refreshSubscribers = [];
}

function onRefreshFailed(error) {
  refreshSubscribers.forEach((callback) => callback(null, error));
  refreshSubscribers = [];
}

const wait = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
const RETRYABLE_STATUS_CODES = [408, 429, 500, 502, 503, 504];

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 500) {
      console.warn("Internal server error.");
    }

    const retryCount = originalRequest.__retryCount || 0;
    const isRetryableNetworkError =
      !error.response &&
      (error.code === "ECONNABORTED" || error.code === "ETIMEDOUT" || error.message === "Network Error");
    const isRetryableStatus =
      error.response?.status && RETRYABLE_STATUS_CODES.includes(error.response.status);

    if ((isRetryableNetworkError || isRetryableStatus) && retryCount < 2) {
      originalRequest.__retryCount = retryCount + 1;
      await wait(800 * (retryCount + 1));
      return api(originalRequest);
    }

    // Skip refresh for auth endpoints
    if (originalRequest.url?.includes("/auth/")) {
      return Promise.reject(error);
    }

    // Handle 401 Unauthorized
    if (
      error.response?.status === 401 &&
      !originalRequest._retry
    ) {
      originalRequest._retry = true;

      const refreshToken = getRefreshToken();

      if (!refreshToken) {
        clearAuth();
        window.location.href = "/login";
        return Promise.reject(error);
      }

      // Queue requests while refresh is in progress
      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          refreshSubscribers.push((token, refreshError) => {
            if (refreshError) {
              reject(refreshError);
              return;
            }

            originalRequest.headers.Authorization = `Bearer ${token}`;
            resolve(api(originalRequest));
          });
        });
      }

      isRefreshing = true;

      try {
        const result = await authService.refreshToken(refreshToken);

        const newAccessToken = result.access_token;

        setTokens(newAccessToken, refreshToken);

        isRefreshing = false;
        onRefreshed(newAccessToken);

        originalRequest.headers.Authorization = `Bearer ${newAccessToken}`;

        return api(originalRequest);
      } catch (refreshError) {
        isRefreshing = false;
        onRefreshFailed(refreshError);

        clearAuth();
        window.location.href = "/login";

        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

export default api;