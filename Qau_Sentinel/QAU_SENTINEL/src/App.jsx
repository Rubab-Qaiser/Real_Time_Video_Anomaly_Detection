import { AuthProvider } from "@/contexts/AuthContext";
import { SocketProvider } from "@/contexts/SocketContext";
import { useIncidentSocket, useDetectionSocket } from "@/hooks/useSocketEvents";
import AppRoutes from "@/routes/AppRoutes";
import { Toaster } from "sonner";

function GlobalAlerts() {
  useIncidentSocket();
  useDetectionSocket();
  return null;
}

export default function App() {
  return (
    <AuthProvider>
      <SocketProvider>
        <GlobalAlerts />
        <AppRoutes />
        <Toaster
          position="top-right"
          richColors
          closeButton
          theme="dark"
        />
      </SocketProvider>
    </AuthProvider>
  );
}