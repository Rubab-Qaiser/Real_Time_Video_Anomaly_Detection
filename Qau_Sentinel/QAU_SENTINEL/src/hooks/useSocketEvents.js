import { useEffect, useState } from "react";
import { useSocket } from "@/contexts/SocketContext";
import { toast } from "sonner";

export function useCameraSocket() {
  const socket = useSocket();
  const [cameraUpdates, setCameraUpdates] = useState({});
  const [cameraDeletions, setCameraDeletions] = useState([]);

  useEffect(() => {
    // Listen for camera status updates
    const handleCameraStatus = (data) => {
      setCameraUpdates((prev) => ({
        ...prev,
        [data.camera_id]: {
          status: data.status,
          timestamp: data.timestamp,
          camera: data.camera,
        },
      }));

      // Show toast notification
      const statusColor = data.status === "online" ? "green" : "red";
      toast.info(`Camera ${data.camera?.name || data.camera_id} is ${data.status}`, {
        style: { borderColor: data.status === "online" ? "#22c55e" : "#ef4444" },
      });
    };

    // Listen for camera deletions
    const handleCameraDeleted = (data) => {
      setCameraDeletions((prev) => [...prev, data.camera_id]);
      toast.warning(`Camera has been deleted`);
    };

    socket.on("camera_status", handleCameraStatus);
    socket.on("camera_deleted", handleCameraDeleted);

    return () => {
      socket.off("camera_status", handleCameraStatus);
      socket.off("camera_deleted", handleCameraDeleted);
    };
  }, [socket]);

  return { cameraUpdates, cameraDeletions };
}

export function useIncidentSocket() {
  const socket = useSocket();
  const [newIncidents, setNewIncidents] = useState([]);
  const [incidentUpdates, setIncidentUpdates] = useState({});

  useEffect(() => {
    // Listen for new incidents
    const handleNewIncident = (data) => {
      setNewIncidents((prev) => [data.incident, ...prev]);
      
      // Show toast notification
      toast.error(`🚨 New ${data.incident.detection_type} incident detected!`, {
        duration: 5000,
      });
    };

    // Listen for incident updates
    const handleIncidentUpdate = (data) => {
      setIncidentUpdates((prev) => ({
        ...prev,
        [data.incident_id]: {
          status: data.status,
          timestamp: data.timestamp,
          incident: data.incident,
        },
      }));
      
      toast.info(`Incident ${data.incident_id} status: ${data.status}`);
    };

    socket.on("new_incident", handleNewIncident);
    socket.on("incident_update", handleIncidentUpdate);

    return () => {
      socket.off("new_incident", handleNewIncident);
      socket.off("incident_update", handleIncidentUpdate);
    };
  }, [socket]);

  return { newIncidents, incidentUpdates };
}

export function useDetectionSocket() {
  const socket = useSocket();
  const [newDetections, setNewDetections] = useState([]);

  useEffect(() => {
    const handleNewDetection = (data) => {
      setNewDetections((prev) => [data.detection, ...prev]);
      
      toast.info(`🎯 New detection: ${data.detection.type}`, {
        duration: 3000,
      });
    };

    socket.on("new_detection", handleNewDetection);

    return () => {
      socket.off("new_detection", handleNewDetection);
    };
  }, [socket]);

  return { newDetections };
}