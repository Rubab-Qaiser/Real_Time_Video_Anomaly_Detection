import { useCallback, useEffect, useState } from "react";
import cameraService from "@/services/cameraService";

export default function useCameras(search = "", status = "all") {
  const [cameras, setCameras] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // ============= FETCH =============
  const fetchCameras = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      const data = await cameraService.getAll({
        search,
        status: status === "all" ? undefined : status,
      });

      setCameras(Array.isArray(data) ? data : data.items ?? []);
    } catch (err) {
      console.error("Failed to fetch cameras:", err);
      setError(err);
    } finally {
      setLoading(false);
    }
  }, [search, status]);

  // ============= CREATE =============
  const addCamera = useCallback(async (cameraData) => {
    setIsSubmitting(true);
    try {
      const newCamera = await cameraService.create(cameraData);
      setCameras(prev => [...prev, newCamera]);
      return { success: true, data: newCamera };
    } catch (err) {
      console.error("Failed to add camera:", err);
      return { success: false, error: err };
    } finally {
      setIsSubmitting(false);
    }
  }, []);

  // ============= UPDATE =============
  const updateCamera = useCallback(async (id, cameraData) => {
    setIsSubmitting(true);
    try {
      const updated = await cameraService.update(id, cameraData);
      setCameras(prev => prev.map(c => c.id === id ? updated : c));
      return { success: true, data: updated };
    } catch (err) {
      console.error("Failed to update camera:", err);
      return { success: false, error: err };
    } finally {
      setIsSubmitting(false);
    }
  }, []);

  // ============= DELETE =============
  const deleteCamera = useCallback(async (id) => {
    setIsSubmitting(true);
    try {
      await cameraService.delete(id);
      setCameras(prev => prev.filter(c => c.id !== id));
      return { success: true };
    } catch (err) {
      console.error("Failed to delete camera:", err);
      return { success: false, error: err };
    } finally {
      setIsSubmitting(false);
    }
  }, []);

  // ============= AUTO-FETCH =============
  useEffect(() => {
    fetchCameras();
  }, [fetchCameras]);

  return {
    cameras,
    loading,
    error,
    isSubmitting,
    refresh: fetchCameras,
    addCamera,
    updateCamera,
    deleteCamera,
  };
}