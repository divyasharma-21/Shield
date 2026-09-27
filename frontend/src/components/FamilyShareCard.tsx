import React, { useState } from 'react';
import { Users, Share2, Loader2 } from 'lucide-react';
import { TextAnalysisResponse, FamilyShareResponse } from '../api/types';
import { fetchFamilyShareSummary } from '../api/client';
import { ShareSummaryModal } from './ShareSummaryModal';

interface FamilyShareCardProps {
  analysis: TextAnalysisResponse;
}

export const FamilyShareCard: React.FC<FamilyShareCardProps> = ({ analysis }) => {
  const [modalOpen, setModalOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [summary, setSummary] = useState<FamilyShareResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleOpenShare = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetchFamilyShareSummary({
        safety_level: analysis.safety_level,
        suspicious_probability: analysis.suspicious_probability,
        evidence_summary: analysis.explanation.evidence_summary,
        recommended_actions: analysis.recommended_actions,
        disclaimer: analysis.disclaimer
      });
      setSummary(res);
      setModalOpen(true);
    } catch (err: any) {
      setError(err?.message || 'Failed to prepare family summary.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <div className="p-4 sm:p-5 rounded-2xl glass-panel border border-cyan-500/30 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div className="space-y-1">
          <div className="flex items-center gap-2 font-bold text-white text-sm sm:text-base">
            <Users className="w-5 h-5 text-cyan-accent" />
            <span>Family Circle Second Opinion</span>
          </div>
          <p className="text-xs sm:text-sm text-slate-300 max-w-xl">
            Unsure what to do? Share a non-alarmist verification card with a child, parent, or trusted family member so they can help verify before you act.
          </p>
          {error && <p className="text-xs text-red-400">{error}</p>}
        </div>

        <button
          onClick={handleOpenShare}
          disabled={loading}
          className="w-full sm:w-auto py-2.5 px-5 rounded-xl bg-cyan-600 hover:bg-cyan-500 text-white font-semibold text-sm flex items-center justify-center gap-2 transition-all shadow-md shadow-cyan-950/60 shrink-0 disabled:opacity-50"
        >
          {loading ? (
            <Loader2 className="w-4 h-4 animate-spin" />
          ) : (
            <Share2 className="w-4 h-4" />
          )}
          <span>Ask Family to Verify</span>
        </button>
      </div>

      <ShareSummaryModal
        summary={summary}
        isOpen={modalOpen}
        onClose={() => setModalOpen(false)}
      />
    </>
  );
};
