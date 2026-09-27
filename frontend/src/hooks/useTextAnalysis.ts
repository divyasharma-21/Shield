import { useState, useCallback } from 'react';
import { TextAnalysisRequest, TextAnalysisResponse } from '../api/types';
import { analyzeText, analyzeCallTranscript } from '../api/client';

export function useTextAnalysis() {
  const [result, setResult] = useState<TextAnalysisResponse | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const runAnalysis = useCallback(async (req: TextAnalysisRequest) => {
    setIsLoading(true);
    setError(null);
    setResult(null);

    try {
      let res: TextAnalysisResponse;
      if (req.input_type === 'call_transcript') {
        res = await analyzeCallTranscript(req.text);
      } else {
        res = await analyzeText(req);
      }
      setResult(res);
      return res;
    } catch (err: any) {
      const msg = err?.message || 'An error occurred while analyzing the text.';
      setError(msg);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const reset = useCallback(() => {
    setResult(null);
    setError(null);
    setIsLoading(false);
  }, []);

  return { runAnalysis, result, isLoading, error, reset };
}
