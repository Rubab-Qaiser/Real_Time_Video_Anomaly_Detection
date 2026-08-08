import { useCallback, useEffect, useState } from "react";
import userService from "@/services/userService";

export default function useUsers(search = "") {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // ============= FETCH =============
  const fetchUsers = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      const data = await userService.getAll({ search });
      setUsers(Array.isArray(data) ? data : data.items ?? []);
    } catch (err) {
      console.error("Failed to fetch users:", err);
      setError(err);
    } finally {
      setLoading(false);
    }
  }, [search]);

  // ============= CREATE =============
  const addUser = useCallback(async (userData) => {
    setIsSubmitting(true);
    try {
      const newUser = await userService.create(userData);
      setUsers(prev => [...prev, newUser]);
      return { success: true, data: newUser };
    } catch (err) {
      console.error("Failed to add user:", err);
      return { success: false, error: err };
    } finally {
      setIsSubmitting(false);
    }
  }, []);

  // ============= UPDATE =============
  const updateUser = useCallback(async (id, userData) => {
    setIsSubmitting(true);
    try {
      const updated = await userService.update(id, userData);
      setUsers(prev => prev.map(u => u.id === id ? updated : u));
      return { success: true, data: updated };
    } catch (err) {
      console.error("Failed to update user:", err);
      return { success: false, error: err };
    } finally {
      setIsSubmitting(false);
    }
  }, []);

  // ============= DELETE =============
  const deleteUser = useCallback(async (id) => {
    setIsSubmitting(true);
    try {
      await userService.delete(id);
      setUsers(prev => prev.filter(u => u.id !== id));
      return { success: true };
    } catch (err) {
      console.error("Failed to delete user:", err);
      return { success: false, error: err };
    } finally {
      setIsSubmitting(false);
    }
  }, []);

  // ============= AUTO-FETCH =============
  useEffect(() => {
    fetchUsers();
  }, [fetchUsers]);

  return {
    users,
    loading,
    error,
    isSubmitting,
    refresh: fetchUsers,
    addUser,
    updateUser,
    deleteUser,
  };
}