import React, { useState } from 'react';
import { ChevronDown, ChevronUp, Code, Copy, Check } from 'lucide-react';
import { TextAnalysisResponse } from '../api/types';

interface TechnicalDetailsProps {
  data: TextAnalysisResponse;
}

export const TechnicalDetails: React.FC<TechnicalDetailsProps> = ({ data }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [copied, setCopied] = useState(false);

  const jsonStr = JSON.stringify(data, null, 2);

  const handleCopyJson = async () => {
    try {
      await navigator.clipboard.writeText(jsonStr);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      // Ignored
    }
  };

  return (
    <div className="rounded-xl border border-surface-border bg-surface overflow-hidden">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full px-4 py-3 flex items-center justify-between text-xs font-medium text-slate-400 hover:text-white hover:bg-surface-elevated transition-colors"
      >
        <div className="flex items-center gap-2">
          <Code className="w-4 h-4 text-cyan-accent" />
          <span>Technical Model Details & Raw Inference Payload</span>
        </div>
        {isOpen ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
      </button>

      {isOpen && (
        <div className="p-4 border-t border-surface-border space-y-4 text-xs font-mono">
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-slate-300">
            <div className="p-2 rounded bg-surface-elevated">
              <div className="text-slate-500 text-[10px] uppercase">Model</div>
              <div className="font-semibold text-cyan-300 truncate">V4 TF-IDF + LogReg</div>
            </div>
            <div className="p-2 rounded bg-surface-elevated">
              <div className="text-slate-500 text-[10px] uppercase">Threshold</div>
              <div className="font-semibold text-amber-300">{data.selected_threshold}</div>
            </div>
            <div className="p-2 rounded bg-surface-elevated">
              <div className="text-slate-500 text-[10px] uppercase">Suspicious Prob</div>
              <div className="font-semibold text-white">{data.suspicious_probability}</div>
            </div>
            <div className="p-2 rounded bg-surface-elevated">
              <div className="text-slate-500 text-[10px] uppercase">Predicted Label</div>
              <div className="font-semibold text-slate-200">{data.predicted_label}</div>
            </div>
          </div>

          <div className="relative">
            <div className="flex items-center justify-between pb-1 text-slate-400">
              <span>Full JSON Response:</span>
              <button
                onClick={handleCopyJson}
                className="flex items-center gap-1 px-2 py-0.5 rounded bg-surface-elevated hover:bg-slate-800 text-cyan-300 text-[11px]"
              >
                {copied ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3" />}
                <span>{copied ? 'Copied JSON' : 'Copy JSON'}</span>
              </button>
            </div>
            <pre className="p-3 rounded-lg bg-black/60 text-slate-300 overflow-x-auto text-[11px] max-h-60 border border-surface-border">
              {jsonStr}
            </pre>
          </div>
        </div>
      )}
    </div>
  );
};
