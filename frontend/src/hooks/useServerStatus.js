import { useEffect, useState } from "react";

export function useServerStatus() {
  const [serverReady, setServerReady] = useState(false);
  const [serverLoading, setServerLoading] = useState(true);

  const API_URL = import.meta.env.VITE_API_URL;

  const ping = async () => {
    console.log("🔵 API_URL:", API_URL);

    try {
      setServerLoading(true);

      const res = await fetch(`${API_URL}/ping/`);

      console.log("Ping status:", res.status);

      if (!res.ok) throw new Error("Server not OK");

      setServerReady(true);
    } catch (err) {
      console.error("Ping failed:", err);

      setServerReady(false);
    } finally {
      setServerLoading(false);
    }
  };

  useEffect(() => {
    ping();
  }, []);

  return {
    serverReady,
    serverLoading,
    retryPing: ping,
  };
}