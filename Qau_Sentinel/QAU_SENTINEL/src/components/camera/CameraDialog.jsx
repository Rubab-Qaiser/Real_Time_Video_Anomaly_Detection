import { useState, useEffect } from "react";

import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

export default function CameraDialog({
  open,
  onOpenChange,
  camera = null,        // null = Add mode, object = Edit mode
  onSave,
}) {
  const [formData, setFormData] = useState({
    name: "",
    location: "",
    source: "",
    status: "Online",
  });

  useEffect(() => {
    if (camera) {
      setFormData({
        name: camera.name || "",
        location: camera.location || "",
        source: camera.source || "",
        status: camera.status || "Online",
      });
    } else {
      setFormData({
        name: "",
        location: "",
        source: "",
        status: "Online",
      });
    }
  }, [camera]);

  const handleSubmit = (e) => {
    e.preventDefault();
    onSave(formData, camera?.id);
    onOpenChange(false);
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>
            {camera ? "Edit Camera" : "Add New Camera"}
          </DialogTitle>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="name">Camera Name</Label>
            <Input
              id="name"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              placeholder="Main Entrance Camera"
              required
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="location">Location</Label>
            <Input
              id="location"
              value={formData.location}
              onChange={(e) => setFormData({ ...formData, location: e.target.value })}
              placeholder="Gate A, Building 1"
              required
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="source">RTSP / Source URL</Label>
            <Input
              id="source"
              value={formData.source}
              onChange={(e) => setFormData({ ...formData, source: e.target.value })}
              placeholder="rtsp://... or /dev/video0"
              required
            />
          </div>

          <div className="space-y-2">
            <Label>Status</Label>
            <Select value={formData.status} onValueChange={(value) => setFormData({ ...formData, status: value })}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="Online">Online</SelectItem>
                <SelectItem value="Offline">Offline</SelectItem>
                <SelectItem value="Maintenance">Maintenance</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className="flex justify-end gap-3 pt-4">
            <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
              Cancel
            </Button>
            <Button type="submit">
              {camera ? "Save Changes" : "Add Camera"}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
}