import React from 'react';
import { ShieldAlert, Lock, CheckCircle2 } from 'lucide-react';

interface ConsentNoticeProps {
  type?: 'text' | 'audio';
}

export const ConsentNotice: React.FC<ConsentNoticeProps> = ({ type = 'text' }) => {
  if (type === 'audio') {
    return (
      <div className="p-4 rounded-xl bg-cyan-950/40 border border-cyan-500/30 text-slate-300 text-xs sm:text-sm space-y-2">
        <div className="flex items-center gap-2 font-semibold text-cyan-300">
          <Lock className="w-4 h-4 text-cyan-accent" />
          <span>Voluntary Recording Consent & Privacy Boundaries</span>
        </div>
        <p className="text-slate-300 leading-relaxed">
          Audio upload is <strong>100% voluntary and user-initiated</strong>. SentryMesh never records background calls,
          never intercepts incoming phone audio, and never accesses your microphone without explicit browser approval.
          Uploaded audio files are processed in temporary memory and immediately deleted after analysis.
        </p>
        <div className="flex items-center gap-2 text-cyan-400 font-medium">
          <CheckCircle2 className="w-3.5 h-3.5" />
          <span>Zero audio retention guarantee. No background listening.</span>
        </div>
      </div>
    );
  }

  return (
    <div className="p-4 rounded-xl bg-amber-950/30 border border-amber-500/30 text-amber-200 text-xs sm:text-sm flex items-start gap-3">
      <ShieldAlert className="w-5 h-5 text-amber-400 shrink-0 mt-0.5" />
      <div className="space-y-1">
        <div className="font-semibold text-amber-300">Safety & Privacy Warning</div>
        <p className="text-amber-200/90 leading-relaxed">
          <strong>Do not enter OTPs, passwords, UPI PINs, card numbers, or private credentials.</strong> SentryMesh does not need sensitive credentials to assess fraud patterns. Submitted text is processed in-memory only.
        </p>
      </div>
    </div>
  );
};
