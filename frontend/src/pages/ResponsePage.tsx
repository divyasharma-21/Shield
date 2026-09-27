import React from 'react';
import { ResponseActionsCard } from '../components/ResponseActionsCard';
import { Disclaimer } from '../components/Disclaimer';
import { AlertTriangle, ShieldCheck } from 'lucide-react';

export const ResponsePage: React.FC = () => {
  return (
    <div className="max-w-5xl mx-auto py-6 sm:py-10 px-4 space-y-8">

      {/* Title */}
      <div className="space-y-2 text-center sm:text-left">
        <div className="flex items-center justify-center sm:justify-start gap-2 text-amber-400 font-semibold text-xs sm:text-sm tracking-wide uppercase">
          <AlertTriangle className="w-4 h-4 text-amber-400" />
          <span>Safety Playbook & Emergency Directives</span>
        </div>
        <h1 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight">
          How to Respond Safely
        </h1>
        <p className="text-sm sm:text-base text-slate-300 max-w-3xl leading-relaxed">
          When dealing with a high-pressure caller or urgent message, following these calm, verified protocols protects you and your family from financial loss.
        </p>
      </div>

      {/* Main Response Actions Card */}
      <ResponseActionsCard />

      {/* Mandatory Disclaimer */}
      <Disclaimer />

    </div>
  );
};
