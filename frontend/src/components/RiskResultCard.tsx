import React from 'react';
import { TextAnalysisResponse } from '../api/types';
import { getSafetyMeta } from '../utils/safetyLabels';
import { formatProbabilityPercent, formatInputTypeLabel } from '../utils/formatters';
import { EvidencePanel } from './EvidencePanel';
import { GuidancePanel } from './GuidancePanel';
import { FamilyShareCard } from './FamilyShareCard';
import { TechnicalDetails } from './TechnicalDetails';
import { Disclaimer } from './Disclaimer';
import { AlertOctagon, AlertTriangle, HelpCircle, ShieldCheck } from 'lucide-react';

interface RiskResultCardProps {
  result: TextAnalysisResponse;
}

export const RiskResultCard: React.FC<RiskResultCardProps> = ({ result }) => {
  const meta = getSafetyMeta(result.safety_level);
  const probPercent = formatProbabilityPercent(result.suspicious_probability);
  const thresholdPercent = formatProbabilityPercent(result.selected_threshold);

  const renderIcon = () => {
    switch (meta.iconName) {
      case 'AlertOctagon':
        return <AlertOctagon className="w-8 h-8 text-red-400" />;
      case 'AlertTriangle':
        return <AlertTriangle className="w-8 h-8 text-amber-400" />;
      case 'HelpCircle':
        return <HelpCircle className="w-8 h-8 text-violet-400" />;
      case 'ShieldCheck':
        return <ShieldCheck className="w-8 h-8 text-emerald-400" />;
      default:
        return <AlertTriangle className="w-8 h-8 text-amber-400" />;
    }
  };

  return (
    <div className={`p-6 sm:p-8 rounded-3xl glass-panel border ${meta.borderClass} ${meta.glowClass} space-y-6 transition-all`}>

      {/* Top Header Badge & Probability */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-surface-border">
        <div className="flex items-start gap-4">
          <div className={`p-3 rounded-2xl ${meta.bgClass} border ${meta.borderClass} shrink-0`}>
            {renderIcon()}
          </div>
          <div className="space-y-1">
            <div className="flex items-center gap-2 flex-wrap">
              <span className={`px-2.5 py-0.5 rounded-full text-xs font-black tracking-wider uppercase ${meta.bgClass} ${meta.colorClass} border ${meta.borderClass}`}>
                {meta.badgeText}
              </span>
              <span className="text-xs text-slate-400 font-mono">
                Channel: {formatInputTypeLabel(result.input_type)}
              </span>
            </div>
            <h3 className="text-xl sm:text-2xl font-bold text-white tracking-tight">
              {meta.title}
            </h3>
            <p className="text-xs sm:text-sm text-slate-300 font-medium">
              {meta.parentLabel}
            </p>
          </div>
        </div>

        {/* Probability Card */}
        <div className="flex sm:flex-col items-center sm:items-end justify-between sm:justify-center p-3 sm:p-0 bg-surface sm:bg-transparent rounded-xl border sm:border-0 border-surface-border">
          <div className="text-left sm:text-right">
            <div className="text-xs text-slate-400 font-medium">Suspicious Risk Score</div>
            <div className={`text-2xl sm:text-3xl font-extrabold font-mono tracking-tight ${meta.colorClass}`}>
              {probPercent}
            </div>
          </div>
          <div className="text-right text-[11px] text-slate-400 font-mono mt-0.5">
            Active Threshold: <span className="text-cyan-300 font-semibold">{thresholdPercent}</span>
          </div>
        </div>
      </div>

      {/* Guidance & Explanation */}
      <GuidancePanel
        explanation={result.explanation}
        actions={result.recommended_actions}
      />

      {/* Model-Derived Evidence Attribution */}
      <EvidencePanel evidence={result.model_evidence} />

      {/* Family Circle Share Action */}
      <FamilyShareCard analysis={result} />

      {/* Technical Details Accordion */}
      <TechnicalDetails data={result} />

      {/* Mandatory Disclaimer */}
      <Disclaimer customText={result.disclaimer} />

    </div>
  );
};
