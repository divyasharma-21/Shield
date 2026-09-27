import React from 'react';
import { Shield, Loader2 } from 'lucide-react';

interface LoadingStateProps {
  message?: string;
}

export const LoadingState: React.FC<LoadingStateProps> = ({
  message = 'Evaluating communication against real V4 model patterns...'
}) => {
  return (
    <div className="p-8 rounded-2xl glass-panel border border-cyan-500/30 flex flex-col items-center justify-center text-center space-y-4">
      <div className="relative">
        <div className="w-16 h-16 rounded-2xl bg-cyan-950/70 border border-cyan-500/50 flex items-center justify-center text-cyan-400">
          <Shield className="w-8 h-8 animate-pulse text-cyan-accent" />
        </div>
        <Loader2 className="w-6 h-6 text-cyan-light animate-spin absolute -bottom-2 -right-2" />
      </div>
      <div className="space-y-1">
        <h4 className="font-semibold text-white text-base">Analyzing Security Vectors</h4>
        <p className="text-sm text-slate-300 max-w-md">{message}</p>
      </div>
    </div>
  );
};
