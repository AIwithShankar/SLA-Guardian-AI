import { useEffect, useState } from "react";
import { getHealth } from "../api/health";

export function useHealth() {
  const [health, setHealth] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    getHealth()
      .then(setHealth)
      .catch((requestError) => setError(requestError.message));
  }, []);

  return { health, error };
}
