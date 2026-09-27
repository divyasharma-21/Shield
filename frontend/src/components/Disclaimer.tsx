import React from 'react';
import { Info } from 'lucide-react';

interface DisclaimerProps {
  customText?: string;
  className?: string;
}

export const Disclaimer: React.FC<DisclaimerProps> = ({ customText, className = '' }) => {
  return (
    <div className={`p-4 rounded-xl bg-surface border border-surface-border text-xs text-slate-400 flex items-start gap-3 ${className}`}>
      <Info className="w-4 h-4 text-cyan-accent shrink-0 mt-0.5" />
      <div className="space-y-1">
        <span className="font-semibold text-slate-300">Important Advisory & Limitations:</span>
        <p className="leading-relaxed">
          {customText ||
            "This is a text-based risk assessment, not proof that a caller, message, payment request, or voice is safe or fraudulent. SentryMesh provides situational awareness to help you pause and verify; it cannot guarantee identity or safety. Always verify independently through trusted channels before taking any financial action."}
        </p>
      </div>
    </div>
  );
};
