import React from 'react';
import { ExplanationBlock } from '../api/types';
import { Lightbulb, ShieldCheck } from 'lucide-react';

interface GuidancePanelProps {
  explanation: ExplanationBlock;
  actions: string[];
}

export const GuidancePanel: React.FC<GuidancePanelProps> = ({ explanation, actions }) => {
  return (
    <div className="space-y-6">

      {/* Plain Language Summary */}
      <div className="p-4 rounded-xl bg-surface-elevated/80 border border-surface-border space-y-3">
        <div className="flex items-center gap-2 text-cyan-300 font-semibold text-sm">
          <Lightbulb className="w-4 h-4 text-cyan-accent" />
          <span>Why Did The Model Reach This Result?</span>
        </div>
        <p className="text-sm text-slate-200 leading-relaxed">
          {explanation.summary}
        </p>

        {explanation.evidence_summary && explanation.evidence_summary.length > 0 && (
          <ul className="space-y-1.5 pt-2 border-t border-surface-border/60 text-xs text-slate-300">
            {explanation.evidence_summary.map((pt, idx) => (
              <li key={idx} className="flex items-start gap-2">
                <span className="text-cyan-400 font-bold">•</span>
                <span>{pt}</span>
              </li>
            ))}
          </ul>
        )}

        <div className="pt-2 text-xs text-slate-400 italic">
          {explanation.uncertainty_note}
        </div>
      </div>

      {/* Recommended Safety Actions */}
      <div className="p-4 rounded-xl bg-surface border border-surface-border space-y-3">
        <div className="flex items-center gap-2 text-amber-300 font-semibold text-sm">
          <ShieldCheck className="w-4 h-4 text-amber-400" />
          <span>Recommended Next Actions for Family Safety</span>
        </div>
        <ul className="space-y-2 text-xs sm:text-sm text-slate-200">
          {actions.map((act, idx) => (
            <li key={idx} className="flex items-start gap-2.5 p-2 rounded-lg bg-surface-elevated/50">
              <span className="w-5 h-5 rounded-full bg-cyan-950 text-cyan-400 flex items-center justify-center shrink-0 text-xs font-bold border border-cyan-800">
                {idx + 1}
              </span>
              <span className="leading-snug">{act}</span>
            </li>
          ))}
        </ul>
      </div>

    </div>
  );
};
