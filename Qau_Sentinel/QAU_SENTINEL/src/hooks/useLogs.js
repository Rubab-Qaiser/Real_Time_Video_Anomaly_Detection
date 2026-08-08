import { useState, useEffect, useCallback } from "react";

import logsService from "@/services/logsService";

export default function useLogs() {
  const [logs, setLogs] = useState([]);
  const [totalPages, setTotalPages] = useState(1);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const [search, setSearch] = useState("");
  const [level, setLevel] = useState("All");
  const [page, setPage] = useState(1);

  const fetchLogs = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await logsService.getLogs({
        page,
        search: search || undefined,
        severity: level === "All" ? undefined : level,
      });

      setLogs(Array.isArray(response.items) ? response.items : []);
      setTotalPages(response.pages ?? 1);
    } catch (err) {
      console.error("Failed to fetch logs:", err);
      setError(err);
    } finally {
      setLoading(false);
    }
  }, [page, search, level]);

  useEffect(() => {
    fetchLogs();
  }, [fetchLogs]);

  return {
    logs,
    loading,
    error,

    search,
    level,
    page,
    totalPages,

    setSearch,
    setLevel,
    setPage,

    refresh: fetchLogs,
  };
}