import React, { useState } from 'react';
import { X, Share2, Copy, Check, ShieldAlert } from 'lucide-react';
import { FamilyShareResponse } from '../api/types';
import { shareOrCopySummary, ShareResult } from '../utils/shareSummary';

interface ShareSummaryModalProps {
  summary: FamilyShareResponse | null;
  isOpen: boolean;
  onClose: () => void;
}

export const ShareSummaryModal: React.FC<ShareSummaryModalProps> = ({
  summary,
  isOpen,
  onClose
}) => {
  const [shareStatus, setShareStatus] = useState<ShareResult | null>(null);

  if (!isOpen || !summary) return null;

  const handleShareClick = async () => {
    const result = await shareOrCopySummary(summary.full_share_text, summary.title);
    setShareStatus(result);
    if (result === 'copied') {
      setTimeout(() => setShareStatus(null), 3000);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-fade-in">
      <div className="bg-surface border border-surface-border rounded-2xl max-w-lg w-full p-6 shadow-2xl space-y-4">

        <div className="flex items-center justify-between pb-3 border-b border-surface-border">
          <div className="flex items-center gap-2">
            <ShieldAlert className="w-5 h-5 text-cyan-accent" />
            <h3 className="font-bold text-white text-base">Share with Family Circle</h3>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-lg text-slate-400 hover:text-white hover:bg-surface-elevated"
            aria-label="Close modal"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <p className="text-xs text-slate-300">
          This preview contains only safety assessment guidance and model facts. SentryMesh never auto-sends messages or accesses phone contacts.
        </p>

        {/* Card Preview */}
        <div className="p-4 rounded-xl bg-surface-elevated border border-surface-border space-y-3 font-sans text-xs">
          <div className="flex items-center justify-between">
            <span className="font-bold text-cyan-300 tracking-wide uppercase text-[11px]">
              {summary.title}
            </span>
            <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-amber-950 text-amber-300 border border-amber-800">
              {summary.safety_level_display}
            </span>
          </div>

          <div className="space-y-1">
            <div className="font-semibold text-slate-300">Why was this flagged:</div>
            <p className="text-slate-400 leading-relaxed">{summary.why_text}</p>
          </div>

          <div className="space-y-1">
            <div className="font-semibold text-slate-300">Action requested from family:</div>
            <p className="text-amber-200/90 leading-relaxed font-medium">{summary.recommended_action_text}</p>
          </div>

          <div className="text-[10px] text-slate-500 pt-2 border-t border-surface-border italic">
            {summary.disclaimer_text}
          </div>
        </div>

        {/* Feedback message */}
        {shareStatus === 'copied' && (
          <div className="p-2.5 rounded-lg bg-emerald-950/60 border border-emerald-500/40 text-emerald-300 text-xs flex items-center gap-2">
            <Check className="w-4 h-4 text-emerald-400" />
            <span>Summary copied to clipboard! You can paste it into WhatsApp or SMS.</span>
          </div>
        )}

        {/* Buttons */}
        <div className="flex flex-col sm:flex-row items-center gap-2 pt-2">
          <button
            onClick={handleShareClick}
            className="w-full sm:flex-1 py-2.5 px-4 rounded-xl bg-cyan-600 hover:bg-cyan-500 text-white font-semibold text-sm flex items-center justify-center gap-2 transition-colors shadow-lg shadow-cyan-950/50"
          >
            <Share2 className="w-4 h-4" />
            <span>Share or Copy Summary</span>
          </button>
          <button
            onClick={onClose}
            className="w-full sm:w-auto py-2.5 px-4 rounded-xl bg-surface-elevated hover:bg-surface border border-surface-border text-slate-300 hover:text-white text-sm font-medium transition-colors"
          >
            Close
          </button>
        </div>

      </div>
    </div>
  );
};
