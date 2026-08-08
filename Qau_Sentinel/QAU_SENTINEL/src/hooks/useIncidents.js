import { useState, useEffect, useCallback } from "react";

import { useSocket } from "@/contexts/SocketContext";
import incidentService from "@/services/incidentService";

export default function useIncidents(
  search = "",
  type = "all",
  severity = "all",
  status = "all",
  initialPage = 1
) {
  const socket = useSocket();
  const [incidents, setIncidents] = useState([]);

  const [pagination, setPagination] = useState({
    page: 1,
    pages: 1,
    total: 0,
  });

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchIncidents = useCallback(
    async (page = 1) => {
      try {
        setError(null);

        const data = await incidentService.getAll({
          search,
          type: type === "all" ? undefined : type,
          severity:
            severity === "all" ? undefined : severity,
          status:
            status === "all" ? undefined : status,
          page,
        });

        setIncidents(
          (data.items ?? []).map((incident) => ({
            ...incident,
            type: incident.detection_type,
          }))
        );

        setPagination({
          page: data.page ?? 1,
          pages: data.pages ?? 1,
          total: data.total ?? 0,
        });
      } catch (err) {
        console.error("Failed to fetch incidents:", err);
        setError(err);
      } finally {
        setLoading(false);
      }
    },
    [search, type, severity, status]
  );

  useEffect(() => {
    fetchIncidents(initialPage);
    const intervalId = window.setInterval(() => fetchIncidents(initialPage), 5000);
    return () => window.clearInterval(intervalId);
  }, [fetchIncidents, initialPage]);

  useEffect(() => {
    const handleNewIncident = (data) => {
      const nextIncident = {
        ...data.incident,
        type: data.incident.detection_type,
      };

      setIncidents((prev) => [nextIncident, ...prev.filter((item) => item.id !== nextIncident.id)]);
      setPagination((prev) => ({ ...prev, total: prev.total + 1 }));
    };

    const handleIncidentUpdate = (data) => {
      setIncidents((prev) =>
        prev.map((incident) =>
          incident.id === Number(data.incident_id)
            ? { ...incident, status: data.status, ...data.incident }
            : incident
        )
      );
    };

    socket.on("new_incident", handleNewIncident);
    socket.on("incident_update", handleIncidentUpdate);

    return () => {
      socket.off("new_incident", handleNewIncident);
      socket.off("incident_update", handleIncidentUpdate);
    };
  }, [socket]);

  return {
    incidents,
    pagination,
    loading,
    error,
    refresh: () => fetchIncidents(pagination.page),
    fetchIncidents,
  };
}