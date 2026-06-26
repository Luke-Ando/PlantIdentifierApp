import { useEffect, useState } from "react";

const API_URL = import.meta.env.VITE_API_URL;

export function useServerStatus() {
  const [serverReady, setServerReady] = useState(false);
  const [serverLoading, setServerLoading] = useState(true);

  const ping = () => {
    setServerLoading(true);

    fetch(`${API_URL}/ping/`)
      .then(() => {
        setServerReady(true);
        setServerLoading(false);
      })
      .catch(() => {
        setServerReady(false);
        setServerLoading(false);
      });
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