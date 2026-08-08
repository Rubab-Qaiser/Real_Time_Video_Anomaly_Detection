import { useState } from "react";

import PageHeader from "@/components/layout/PageHeader";
import { PageTransition } from "@/components/animations";

import CameraToolbar from "@/components/camera/CameraToolbar";
import CameraGrid from "@/components/camera/CameraGrid";

import CameraDialog from "@/components/camera/CameraDialog";
import DeleteCameraDialog from "@/components/camera/DeleteCameraDialog";

import useCameras from "@/hooks/useCameras";

import LoadingSpinner from "@/components/common/LoadingSpinner";
import EmptyState from "@/components/common/EmptyState";
import ErrorState from "@/components/common/ErrorState";

export default function Cameras() {
  const [search, setSearch] = useState("");
  const [status, setStatus] = useState("all");

  // Dialog states
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingCamera, setEditingCamera] = useState(null);

  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [cameraToDelete, setCameraToDelete] = useState(null);

  const {
    cameras,
    loading,
    error,
    refresh,
  } = useCameras(search, status);

  const handleAddCamera = () => {
    setEditingCamera(null);
    setDialogOpen(true);
  };

  const handleEditCamera = (camera) => {
    setEditingCamera(camera);
    setDialogOpen(true);
  };

  const handleDeleteClick = (camera) => {
    setCameraToDelete(camera);
    setDeleteDialogOpen(true);
  };

  const confirmDelete = () => {
    if (cameraToDelete) {
      // TODO: Call delete from service
      console.log("Deleting camera:", cameraToDelete.id);
      refresh();
    }
    setDeleteDialogOpen(false);
    setCameraToDelete(null);
  };

  const handleSaveCamera = (formData, cameraId) => {
    if (cameraId) {
      console.log("Updating camera:", cameraId, formData);
    } else {
      console.log("Creating new camera:", formData);
    }
    refresh();
  };

  if (loading) {
    return <LoadingSpinner text="Loading cameras..." fullScreen />;
  }

  if (error) {
    return (
      <ErrorState
        title="Unable to load cameras"
        description="Please check the camera server and try again."
        onRetry={refresh}
      />
    );
  }

  return (
    <PageTransition>
      <div className="flex flex-col gap-5">

        <PageHeader
          title="Camera Management"
          subtitle="Monitor, manage, and configure surveillance cameras connected to the AI detection system."
        />

        <CameraToolbar
          search={search}
          onSearchChange={setSearch}
          status={status}
          onStatusChange={setStatus}
          onRefresh={refresh}
          onAddCamera={handleAddCamera}
        />

        <CameraGrid
          cameras={cameras}
          onEdit={handleEditCamera}
          onDelete={handleDeleteClick}
        />

        {/* Add / Edit Dialog */}
        <CameraDialog
          open={dialogOpen}
          onOpenChange={setDialogOpen}
          camera={editingCamera}
          onSave={handleSaveCamera}
        />

        {/* Delete Confirmation Dialog */}
        <DeleteCameraDialog
          open={deleteDialogOpen}
          onOpenChange={setDeleteDialogOpen}
          camera={cameraToDelete}
          onConfirm={confirmDelete}
        />

      </div>
    </PageTransition>
  );
}