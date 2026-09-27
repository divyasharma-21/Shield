import React from 'react';
import { AlertCircle, RefreshCw } from 'lucide-react';

interface ErrorStateProps {
  title?: string;
  message: string;
  onRetry?: () => void;
}

export const ErrorState: React.FC<ErrorStateProps> = ({
  title = 'Analysis Request Failed',
  message,
  onRetry
}) => {
  return (
    <div className="p-6 rounded-2xl bg-red-950/40 border border-red-500/40 text-red-200 space-y-3">
      <div className="flex items-center gap-3">
        <AlertCircle className="w-5 h-5 text-red-400 shrink-0" />
        <h4 className="font-semibold text-white text-base">{title}</h4>
      </div>
      <p className="text-sm text-red-200/90 leading-relaxed font-mono bg-red-950/60 p-3 rounded-lg border border-red-900/50">
        {message}
      </p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-surface-elevated hover:bg-surface border border-surface-border text-sm text-white font-medium transition-colors"
        >
          <RefreshCw className="w-4 h-4" />
          <span>Try Again</span>
        </button>
      )}
    </div>
  );
};
