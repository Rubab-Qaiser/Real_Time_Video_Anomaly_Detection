import { useState } from "react";

import PageHeader from "@/components/layout/PageHeader";
import { PageTransition } from "@/components/animations";

import IncidentFilters from "@/components/incidents/IncidentFilters";
import IncidentStats from "@/components/incidents/IncidentStats";
import IncidentTable from "@/components/incidents/IncidentTable";
import Pagination from "@/components/incidents/Pagination";

import useIncidents from "@/hooks/useIncidents";

import LoadingSpinner from "@/components/common/LoadingSpinner";
import EmptyState from "@/components/common/EmptyState";
import ErrorState from "@/components/common/ErrorState";

export default function Incidents() {
  const [search, setSearch] = useState("");
  const [type, setType] = useState("all");
  const [severity, setSeverity] = useState("all");
  const [status, setStatus] = useState("all");

  const {
    incidents: fetchedIncidents,
    pagination,
    loading,
    error,
    refresh,
    fetchIncidents,
  } = useIncidents(search, type, severity, status);

  if (loading) {
    return (
      <LoadingSpinner
        text="Loading incidents..."
        fullScreen
      />
    );
  }

  if (error) {
    return (
      <ErrorState
        title="Unable to load incidents"
        description="Failed to retrieve incident records."
        onRetry={refresh}
      />
    );
  }

  return (
    <PageTransition>
      <div className="flex flex-col gap-5">
        <PageHeader
          title="Incident Management"
          subtitle="Review, monitor, and manage AI-detected incidents across all connected cameras."
        />

        {/* Filters */}
        <IncidentFilters
          search={search}
          onSearchChange={setSearch}
          type={type}
          onTypeChange={setType}
          severity={severity}
          onSeverityChange={setSeverity}
          status={status}
          onStatusChange={setStatus}
          onRefresh={refresh}
          onReset={() => {
            setSearch("");
            setType("all");
            setSeverity("all");
            setStatus("all");
          }}
        />

        {fetchedIncidents.length === 0 ? (
          <EmptyState
            title="No incidents found"
            description="There are currently no incidents matching the selected filters."
          />
        ) : (
          <>
            <IncidentStats incidents={fetchedIncidents} />

            <IncidentTable incidents={fetchedIncidents} />

            <Pagination
              pagination={pagination}
              onPageChange={fetchIncidents}
            />
          </>
        )}
      </div>
    </PageTransition>
  );
}