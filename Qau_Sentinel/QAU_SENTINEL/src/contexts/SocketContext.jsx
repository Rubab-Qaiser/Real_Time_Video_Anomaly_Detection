import { createContext, useContext, useEffect, useState, useRef } from "react";
import { io } from "socket.io-client";
import { useAuth } from "./AuthContext";

const SocketContext = createContext(null);

const SOCKET_URL = (
  import.meta.env.VITE_SOCKET_URL ||
  import.meta.env.VITE_API_URL ||
  "http://localhost:5000"
).replace(/\/api\/?$/, "").replace(/^ws/, "http");

export function SocketProvider({ children }) {
  const { isAuthenticated } = useAuth();
  const [isConnected, setIsConnected] = useState(false);
  const [latencyMs, setLatencyMs] = useState(null);
  const socketRef = useRef(null);
  const latencySamplesRef = useRef([]);
  const pingIntervalRef = useRef(null);

  useEffect(() => {
    // Only connect if user is authenticated
    if (!isAuthenticated) {
      if (socketRef.current) {
        socketRef.current.disconnect();
        socketRef.current = null;
      }
      setIsConnected(false);
      return;
    }

    // Connect to Socket.IO server
    const socket = io(SOCKET_URL, {
      // Flask-SocketIO threading mode reliably supports Engine.IO polling.
      transports: ["polling"],
      withCredentials: true,
    });

    socketRef.current = socket;

    socket.on("connect", () => {
      console.log("🔌 Socket.IO connected");
      setIsConnected(true);
      // start ping/pong latency sampling
      socket.on("latency_pong", (data) => {
        try {
          const now = Date.now();
          const clientTs = data && data.client_ts ? data.client_ts : null;
          if (clientTs) {
            const rtt = now - clientTs;
            const samples = latencySamplesRef.current;
            samples.push(rtt);
            if (samples.length > 20) samples.shift();
            latencySamplesRef.current = samples;
            const avg = Math.round(samples.reduce((a, b) => a + b, 0) / samples.length);
            setLatencyMs(avg);
          }
        } catch (e) {
          // ignore
        }
      });

      pingIntervalRef.current = setInterval(() => {
        try {
          socket.emit("latency_ping", { client_ts: Date.now() });
        } catch (e) {}
      }, 5000);
    });

    socket.on("disconnect", () => {
      console.log("🔌 Socket.IO disconnected");
      setIsConnected(false);
    });

    socket.on("connected", (data) => {
      console.log("📢 Socket.IO:", data.message);
    });

    return () => {
      socket.disconnect();
      socketRef.current = null;
      setIsConnected(false);
      // cleanup latency interval and listeners
      if (pingIntervalRef.current) {
        clearInterval(pingIntervalRef.current);
        pingIntervalRef.current = null;
      }
      if (socket) {
        socket.off("latency_pong");
      }
    };
  }, [isAuthenticated]);

  // Listen to events
  const on = (event, callback) => {
    if (socketRef.current) {
      socketRef.current.on(event, callback);
    }
  };

  const off = (event, callback) => {
    if (socketRef.current) {
      socketRef.current.off(event, callback);
    }
  };

  const emit = (event, data) => {
    if (socketRef.current) {
      socketRef.current.emit(event, data);
    }
  };

  const value = {
    socket: socketRef.current,
    isConnected,
    on,
    off,
    emit,
    latencyMs,
  };

  return (
    <SocketContext.Provider value={value}>
      {children}
    </SocketContext.Provider>
  );
}

export function useSocket() {
  const context = useContext(SocketContext);
  if (!context) {
    throw new Error("useSocket must be used within a SocketProvider");
  }
  return context;
}