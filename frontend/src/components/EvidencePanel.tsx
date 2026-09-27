import React from 'react';
import { ModelEvidence } from '../api/types';
import { formatContribution } from '../utils/formatters';
import { TrendingUp, TrendingDown, HelpCircle } from 'lucide-react';

interface EvidencePanelProps {
  evidence: ModelEvidence;
}

export const EvidencePanel: React.FC<EvidencePanelProps> = ({ evidence }) => {
  const hasSuspicious = evidence.signals_favoring_suspicious && evidence.signals_favoring_suspicious.length > 0;
  const hasLegitimate = evidence.signals_favoring_legitimate && evidence.signals_favoring_legitimate.length > 0;

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h4 className="text-sm font-semibold uppercase tracking-wider text-slate-300 flex items-center gap-2">
          <span>Model-Derived Feature Attribution</span>
          <span className="text-xs font-normal text-slate-500 lowercase">(TF-IDF × LogisticRegression weights)</span>
        </h4>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">

        {/* Suspicious Signals */}
        <div className="p-4 rounded-xl bg-surface border border-red-500/20 space-y-3">
          <div className="flex items-center justify-between pb-2 border-b border-surface-border">
            <span className="text-xs font-semibold text-red-400 flex items-center gap-1.5">
              <TrendingUp className="w-3.5 h-3.5" />
              Signals Favoring Suspicious
            </span>
            <span className="text-xs text-slate-500">Weight Impact</span>
          </div>

          {hasSuspicious ? (
            <div className="space-y-2">
              {evidence.signals_favoring_suspicious.map((item, idx) => (
                <div key={idx} className="flex items-center justify-between p-2 rounded-lg bg-surface-elevated/70 text-xs">
                  <span className="font-mono text-slate-200 truncate pr-2">
                    "{item.feature}"
                  </span>
                  <span className="font-mono font-medium text-red-400 shrink-0">
                    {formatContribution(item.contribution)}
                  </span>
                </div>
              ))}
            </div>
          ) : (
            <div className="py-4 text-center text-xs text-slate-500 flex flex-col items-center gap-1">
              <HelpCircle className="w-4 h-4 text-slate-600" />
              <span>No dominant suspicious vocabulary markers isolated.</span>
            </div>
          )}
        </div>

        {/* Legitimate Signals */}
        <div className="p-4 rounded-xl bg-surface border border-emerald-500/20 space-y-3">
          <div className="flex items-center justify-between pb-2 border-b border-surface-border">
            <span className="text-xs font-semibold text-emerald-400 flex items-center gap-1.5">
              <TrendingDown className="w-3.5 h-3.5" />
              Signals Favoring Legitimate
            </span>
            <span className="text-xs text-slate-500">Weight Impact</span>
          </div>

          {hasLegitimate ? (
            <div className="space-y-2">
              {evidence.signals_favoring_legitimate.map((item, idx) => (
                <div key={idx} className="flex items-center justify-between p-2 rounded-lg bg-surface-elevated/70 text-xs">
                  <span className="font-mono text-slate-200 truncate pr-2">
                    "{item.feature}"
                  </span>
                  <span className="font-mono font-medium text-emerald-400 shrink-0">
                    {formatContribution(item.contribution)}
                  </span>
                </div>
              ))}
            </div>
          ) : (
            <div className="py-4 text-center text-xs text-slate-500 flex flex-col items-center gap-1">
              <HelpCircle className="w-4 h-4 text-slate-600" />
              <span>No standard legitimate transactional markers isolated.</span>
            </div>
          )}
        </div>

      </div>
    </div>
  );
};
