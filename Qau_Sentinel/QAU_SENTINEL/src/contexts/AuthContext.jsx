import { createContext, useContext, useState, useEffect, useCallback } from "react";
import {
  setTokens,
  getAccessToken,
  getRefreshToken,
  setUser,
  getUser,
  clearAuth,
  isAuthenticated,
  isTokenExpired,
} from "@/utils/token";
import authService from "@/services/authService";

// Create context
const AuthContext = createContext(null);

// Provider component
export function AuthProvider({ children }) {
  const [user, setUserState] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isAuth, setIsAuth] = useState(false);

  // Initialize auth state from localStorage
  useEffect(() => {
    const initAuth = async () => {
      const storedUser = getUser();
      const token = getAccessToken();

      if (storedUser && token && !isTokenExpired(token)) {
        setUserState(storedUser);
        setIsAuth(true);
      } else if (storedUser && token && isTokenExpired(token)) {
        // Token expired - try to refresh
        try {
          const refreshToken = getRefreshToken();
          if (refreshToken) {
            const result = await authService.refreshToken(refreshToken);
            setTokens(result.access_token, refreshToken);
            setUserState(storedUser);
            setIsAuth(true);
          } else {
            clearAuth();
            setUserState(null);
            setIsAuth(false);
          }
        } catch {
          clearAuth();
          setUserState(null);
          setIsAuth(false);
        }
      } else {
        clearAuth();
        setUserState(null);
        setIsAuth(false);
      }
      setLoading(false);
    };

    initAuth();
  }, []);

  // Login function
  const login = useCallback(async (email, password) => {
    const result = await authService.login(email, password);
    
    // Store tokens
    setTokens(result.access_token, result.refresh_token);
    setUser(result.user);
    
    // Update state
    setUserState(result.user);
    setIsAuth(true);
    
    return result;
  }, []);

  // Logout function
  const logout = useCallback(async () => {
    try {
      const refreshToken = getRefreshToken();
      if (refreshToken) {
        await authService.logout(refreshToken);
      }
    } catch (error) {
      console.error("Logout error:", error);
    } finally {
      clearAuth();
      setUserState(null);
      setIsAuth(false);
    }
  }, []);

  // Refresh token function
  const refreshAuth = useCallback(async () => {
    try {
      const refreshToken = getRefreshToken();
      if (!refreshToken) {
        throw new Error("No refresh token");
      }
      const result = await authService.refreshToken(refreshToken);
      setTokens(result.access_token, refreshToken);
      return result;
    } catch (error) {
      clearAuth();
      setUserState(null);
      setIsAuth(false);
      throw error;
    }
  }, []);

  // Check if user has a specific role
  const hasRole = useCallback((roles) => {
    if (!user) return false;
    if (typeof roles === "string") {
      return user.role === roles;
    }
    return roles.includes(user.role);
  }, [user]);

  const value = {
    user,
    isAuthenticated: isAuth,
    loading,
    login,
    logout,
    refreshAuth,
    hasRole,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

// Custom hook to use auth context
export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}