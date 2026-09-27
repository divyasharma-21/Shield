import { useState, useCallback } from 'react';
import { AudioAnalysisResponse } from '../api/types';
import { uploadCallAudio, ApiError } from '../api/client';

export function useAudioAnalysis() {
  const [result, setResult] = useState<AudioAnalysisResponse | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [unconfiguredMessage, setUnconfiguredMessage] = useState<string | null>(null);

  const uploadAudio = useCallback(async (file: File) => {
    setIsLoading(true);
    setError(null);
    setUnconfiguredMessage(null);
    setResult(null);

    try {
      const res = await uploadCallAudio(file);
      setResult(res);
      return res;
    } catch (err: any) {
      if (err instanceof ApiError && err.status === 501) {
        setUnconfiguredMessage(
          err.data?.detail?.message ||
          'Audio transcription requires a configured speech-to-text model. No transcript-risk result has been generated.'
        );
      } else {
        setError(err?.message || 'Failed to process audio file.');
      }
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const reset = useCallback(() => {
    setResult(null);
    setError(null);
    setUnconfiguredMessage(null);
    setIsLoading(false);
  }, []);

  return { uploadAudio, result, isLoading, error, unconfiguredMessage, reset };
}
