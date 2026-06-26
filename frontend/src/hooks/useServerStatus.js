import { useEffect, useRef, useState } from "react";

export function useServerStatus() {
  const [serverReady, setServerReady] = useState(false);
  const [serverLoading, setServerLoading] = useState(true);

  const API_URL = import.meta.env.VITE_API_URL;

  const ran = useRef(false);

  const ping = async () => {
    console.log("API_URL =", API_URL);

    if (!API_URL) {
      console.error("VITE_API_URL is missing");
      setServerLoading(false);
      setServerReady(false);
      return;
    }

    try {
      setServerLoading(true);

      const res = await fetch(`${API_URL}/ping/`);

      console.log("ping status:", res.status);

      setServerReady(res.ok);
    } catch (err) {
      console.error("ping failed:", err);
      setServerReady(false);
    } finally {
      setServerLoading(false);
    }
  };

  useEffect(() => {
    if (ran.current) return;
    ran.current = true;
    ping();
  }, []);

  return { serverReady, serverLoading, retryPing: ping };
}