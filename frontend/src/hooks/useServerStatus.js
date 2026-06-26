import { useEffect, useRef, useState } from "react";

export function useServerStatus() {
  const [serverReady, setServerReady] = useState(false);
  const [serverLoading, setServerLoading] = useState(true);

  const API_URL = import.meta.env.VITE_API_URL;
  const didRun = useRef(false);

  const ping = async () => {
    try {
      setServerLoading(true);

      const res = await fetch(`${API_URL}/ping/`);

      if (!res.ok) throw new Error("Ping failed");

      setServerReady(true);
    } catch (err) {
      setServerReady(false);
    } finally {
      setServerLoading(false);
    }
  };

  useEffect(() => {
    if (didRun.current) return; // prevents StrictMode double run issues
    didRun.current = true;

    ping();
  }, []);

  return { serverReady, serverLoading, retryPing: ping };
}