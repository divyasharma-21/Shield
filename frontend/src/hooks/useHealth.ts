import { useState, useEffect, useCallback } from 'react';
import { HealthResponse } from '../api/types';
import { fetchHealth } from '../api/client';

export function useHealth() {
  const [data, setData] = useState<HealthResponse | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const checkHealth = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const res = await fetchHealth();
      setData(res);
    } catch (err: any) {
      setError(err?.message || 'Unable to connect to SentryMesh backend service.');
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    checkHealth();
  }, [checkHealth]);

  return { data, isLoading, error, refetch: checkHealth };
}
