import { useState, useMemo } from "react";

import PageHeader from "@/components/layout/PageHeader";
import CameraToolbar from "@/components/camera/CameraToolbar";
import CameraGrid from "@/components/camera/CameraGrid";

// ✅ Using the correct path based on your file structure
// You shared these files from: src/components/cameras/
import CameraDialog from "@/components/camera/CameraDialog";
import DeleteCameraDialog from "@/components/camera/DeleteCameraDialog";

import { PageTransition } from "@/components/animations";
import LoadingSpinner from "@/components/common/LoadingSpinner";
import EmptyState from "@/components/common/EmptyState";
import ErrorState from "@/components/common/ErrorState";
import useCameras from "@/hooks/useCameras";
import { useCameraSocket } from "@/hooks/useSocketEvents"; // ✅ Socket hook

// sonner is already installed
import { toast } from "sonner";

export default function Cameras() {
  // ============= STATE =============
  const [search, setSearch] = useState("");
  const [status, setStatus] = useState("all");

  const [addDialogOpen, setAddDialogOpen] = useState(false);
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [selectedCamera, setSelectedCamera] = useState(null);

  // ============= HOOK =============
  const {
    cameras: fetchedCameras,
    loading,
    error,
    refresh,
    addCamera,
    updateCamera,
    deleteCamera,
    isSubmitting,
  } = useCameras(search, status);

  // ============= SOCKET =============
  const { cameraUpdates, cameraDeletions } = useCameraSocket();

  // ✅ Merge live socket updates/deletions on top of the fetched camera list,
  // without needing a setCameras from useCameras.
  const cameras = useMemo(() => {
    return fetchedCameras
      .filter((camera) => !cameraDeletions.includes(camera.id))
      .map((camera) => {
        const update = cameraUpdates[camera.id];
        return update ? { ...camera, status: update.status } : camera;
      })
      .slice(0, 4);
  }, [fetchedCameras, cameraUpdates, cameraDeletions]);

  // ============= HANDLERS =============
  const handleAddCamera = () => {
    setSelectedCamera(null);
    setAddDialogOpen(true);
  };

  const handleEditCamera = (camera) => {
    setSelectedCamera(camera);
    setEditDialogOpen(true);
  };

  const handleDeleteCamera = (camera) => {
    setSelectedCamera(camera);
    setDeleteDialogOpen(true);
  };

  const handleSaveCamera = async (formData, cameraId) => {
    let result;

    if (cameraId) {
      // EDIT
      result = await updateCamera(cameraId, formData);
      if (result.success) {
        toast.success(`Camera "${formData.name}" updated successfully!`);
        setEditDialogOpen(false);
      } else {
        toast.error("Failed to update camera. Please try again.");
      }
    } else {
      // ADD
      result = await addCamera(formData);
      if (result.success) {
        toast.success(`Camera "${formData.name}" added successfully!`);
        setAddDialogOpen(false);
      } else {
        toast.error("Failed to add camera. Please try again.");
      }
    }
  };

  const handleDeleteConfirm = async () => {
    if (!selectedCamera) return;

    const result = await deleteCamera(selectedCamera.id);
    if (result.success) {
      toast.success(`Camera "${selectedCamera.name}" deleted successfully!`);
      setDeleteDialogOpen(false);
      setSelectedCamera(null);
    } else {
      toast.error("Failed to delete camera. Please try again.");
    }
  };

  // ============= RENDER =============

  // Loading
  if (loading) {
    return <LoadingSpinner text="Loading cameras..." fullScreen />;
  }

  // Error
  if (error) {
    return (
      <ErrorState
        title="Unable to load cameras"
        description="Please check the camera server and try again."
        onRetry={refresh}
      />
    );
  }

  // Empty (with toolbar for adding)
  if (!cameras.length) {
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
          <EmptyState
            title="No Cameras Found"
            description="No cameras are currently available. Click 'Add Camera' to get started."
          />
          <CameraDialog
            open={addDialogOpen}
            onOpenChange={setAddDialogOpen}
            camera={null}
            onSave={handleSaveCamera}
          />
        </div>
      </PageTransition>
    );
  }

  // Main view
  return (
    <PageTransition>
      <div className="flex flex-col gap-5">
        {/* Header */}
        <PageHeader
          title="Camera Management"
          subtitle="Monitor, manage, and configure surveillance cameras connected to the AI detection system."
        />

        {/* Toolbar */}
        <CameraToolbar
          search={search}
          onSearchChange={setSearch}
          status={status}
          onStatusChange={setStatus}
          onRefresh={refresh}
          onAddCamera={handleAddCamera}
        />

        {/* Grid */}
        <CameraGrid
          cameras={cameras}
          onEdit={handleEditCamera}
          onDelete={handleDeleteCamera}
        />

        {/* Dialogs */}
        <CameraDialog
          open={addDialogOpen}
          onOpenChange={setAddDialogOpen}
          camera={null}
          onSave={handleSaveCamera}
        />

        <CameraDialog
          open={editDialogOpen}
          onOpenChange={setEditDialogOpen}
          camera={selectedCamera}
          onSave={handleSaveCamera}
        />

        <DeleteCameraDialog
          open={deleteDialogOpen}
          onOpenChange={setDeleteDialogOpen}
          camera={selectedCamera}
          onConfirm={handleDeleteConfirm}
        />
      </div>
    </PageTransition>
  );
}
