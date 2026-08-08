import { useState } from "react";

import PageHeader from "@/components/layout/PageHeader";
import UserTable from "@/components/users/UserTable";
import UserDialog from "@/components/users/UserDialog";
import DeleteUserDialog from "@/components/users/DeleteUserDialog";
import { PageTransition } from "@/components/animations";
import LoadingSpinner from "@/components/common/LoadingSpinner";
import EmptyState from "@/components/common/EmptyState";
import ErrorState from "@/components/common/ErrorState";
import useUsers from "@/hooks/useUsers";

import { toast } from "sonner";

export default function Users() {
  // ============= STATE =============
  const [search, setSearch] = useState("");
  const [addDialogOpen, setAddDialogOpen] = useState(false);
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [selectedUser, setSelectedUser] = useState(null);

  // ============= HOOK =============
  const {
    users,
    loading,
    error,
    refresh,
    addUser,
    updateUser,
    deleteUser,
    isSubmitting,
  } = useUsers(search);

  // ============= HANDLERS =============
  const handleAddUser = () => {
    setSelectedUser(null);
    setAddDialogOpen(true);
  };

  const handleEditUser = (user) => {
    setSelectedUser(user);
    setEditDialogOpen(true);
  };

  const handleDeleteUser = (user) => {
    setSelectedUser(user);
    setDeleteDialogOpen(true);
  };

  const handleSaveUser = async (formData, userId) => {
    let result;

    if (userId) {
      // EDIT
      result = await updateUser(userId, formData);
      if (result.success) {
        toast.success(`User "${formData.username}" updated successfully!`);
        setEditDialogOpen(false);
      } else {
        toast.error(result.error?.response?.data?.error || "Failed to update user");
      }
    } else {
      // ADD
      result = await addUser(formData);
      if (result.success) {
        toast.success(`User "${formData.username}" added successfully!`);
        setAddDialogOpen(false);
      } else {
        toast.error(result.error?.response?.data?.error || "Failed to add user");
      }
    }
  };

  const handleDeleteConfirm = async () => {
    if (!selectedUser) return;

    const result = await deleteUser(selectedUser.id);
    if (result.success) {
      toast.success(`User "${selectedUser.username}" deleted successfully!`);
      setDeleteDialogOpen(false);
      setSelectedUser(null);
    } else {
      toast.error(result.error?.response?.data?.error || "Failed to delete user");
    }
  };

  // ============= RENDER =============

  if (loading) {
    return <LoadingSpinner text="Loading users..." fullScreen />;
  }

  if (error) {
    return (
      <ErrorState
        title="Unable to load users"
        description="Please check the server and try again."
        onRetry={refresh}
      />
    );
  }

  if (!users.length) {
    return (
      <PageTransition>
        <div className="flex flex-col gap-5">
          <PageHeader
            title="User Management"
            subtitle="Manage system users and their roles."
          />
          <div className="flex items-center justify-between gap-4">
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search users..."
              className="flex-1 max-w-md rounded-lg border border-slate-700 bg-slate-950 px-4 py-2 text-white focus:outline-none focus:border-blue-500"
            />
            <button
              onClick={handleAddUser}
              className="rounded-lg bg-blue-600 px-4 py-2 text-white hover:bg-blue-700"
            >
              + Add User
            </button>
          </div>
          <EmptyState
            title="No Users Found"
            description="No users are currently available. Click 'Add User' to get started."
          />
          <UserDialog
            open={addDialogOpen}
            onOpenChange={setAddDialogOpen}
            user={null}
            onSave={handleSaveUser}
          />
        </div>
      </PageTransition>
    );
  }

  return (
    <PageTransition>
      <div className="flex flex-col gap-5">
        <PageHeader
          title="User Management"
          subtitle="Manage system users and their roles."
        />

        <div className="flex items-center justify-between gap-4">
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search users..."
            className="flex-1 max-w-md rounded-lg border border-slate-700 bg-slate-950 px-4 py-2 text-white focus:outline-none focus:border-blue-500"
          />
          <button
            onClick={handleAddUser}
            className="rounded-lg bg-blue-600 px-4 py-2 text-white hover:bg-blue-700"
          >
            + Add User
          </button>
        </div>

        <UserTable
          users={users}
          onEdit={handleEditUser}
          onDelete={handleDeleteUser}
        />

        <UserDialog
          open={addDialogOpen}
          onOpenChange={setAddDialogOpen}
          user={null}
          onSave={handleSaveUser}
        />

        <UserDialog
          open={editDialogOpen}
          onOpenChange={setEditDialogOpen}
          user={selectedUser}
          onSave={handleSaveUser}
        />

        <DeleteUserDialog
          open={deleteDialogOpen}
          onOpenChange={setDeleteDialogOpen}
          user={selectedUser}
          onConfirm={handleDeleteConfirm}
        />
      </div>
    </PageTransition>
  );
}