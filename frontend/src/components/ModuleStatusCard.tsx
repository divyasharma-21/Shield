import React from 'react';
import { PhoneCall, Globe, Smartphone, Shield, Radio, CheckCircle2, Clock } from 'lucide-react';
import { useHealth } from '../hooks/useHealth';

export const ModuleStatusCard: React.FC = () => {
  const { data: health } = useHealth();

  return (
    <div className="p-6 sm:p-8 rounded-3xl glass-panel border border-surface-border space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-4 border-b border-surface-border">
        <div>
          <h3 className="text-base sm:text-lg font-bold text-white tracking-tight">
            SentryMesh Defense Grid Architecture
          </h3>
          <p className="text-xs text-slate-400">
            Real-time status of family protection components.
          </p>
        </div>
        <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-cyan-950/80 border border-cyan-500/40 text-xs font-mono text-cyan-300">
          <Radio className="w-3.5 h-3.5 text-cyan-accent animate-pulse" />
          <span>Active Model: {health?.model_name || 'V4 TF-IDF'}</span>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">

        {/* Active Module: ParentCall Guardian */}
        <div className="p-4 rounded-2xl bg-cyan-950/40 border border-cyan-500/50 space-y-3 relative overflow-hidden">
          <div className="flex items-center justify-between">
            <div className="p-2 rounded-xl bg-cyan-900/60 text-cyan-300 border border-cyan-700/50">
              <PhoneCall className="w-5 h-5" />
            </div>
            <span className="flex items-center gap-1 text-[11px] font-bold uppercase tracking-wider text-emerald-400 bg-emerald-950/80 px-2 py-0.5 rounded-full border border-emerald-500/40">
              <CheckCircle2 className="w-3 h-3" />
              Active
            </span>
          </div>
          <div>
            <div className="font-bold text-white text-sm">ParentCall Guardian</div>
            <div className="text-xs text-slate-300 mt-1 leading-relaxed">
              Real-time binary fraud detection with V4 model, calibrated thresholding, and Family Circle verification.
            </div>
          </div>
        </div>

        {/* Future Module: WebGuard */}
        <div className="p-4 rounded-2xl bg-surface border border-surface-border/70 space-y-3 opacity-60">
          <div className="flex items-center justify-between">
            <div className="p-2 rounded-xl bg-surface-elevated text-slate-400 border border-surface-border">
              <Globe className="w-5 h-5" />
            </div>
            <span className="flex items-center gap-1 text-[11px] font-medium text-slate-400 bg-surface-elevated px-2 py-0.5 rounded-full">
              <Clock className="w-3 h-3" />
              Roadmap
            </span>
          </div>
          <div>
            <div className="font-bold text-slate-300 text-sm">WebGuard</div>
            <div className="text-xs text-slate-400 mt-1 leading-relaxed">
              Phishing domain reputation and deceptive banking link inspection (in development).
            </div>
          </div>
        </div>

        {/* Future Module: AppGuard */}
        <div className="p-4 rounded-2xl bg-surface border border-surface-border/70 space-y-3 opacity-60">
          <div className="flex items-center justify-between">
            <div className="p-2 rounded-xl bg-surface-elevated text-slate-400 border border-surface-border">
              <Smartphone className="w-5 h-5" />
            </div>
            <span className="flex items-center gap-1 text-[11px] font-medium text-slate-400 bg-surface-elevated px-2 py-0.5 rounded-full">
              <Clock className="w-3 h-3" />
              Roadmap
            </span>
          </div>
          <div>
            <div className="font-bold text-slate-300 text-sm">AppGuard</div>
            <div className="text-xs text-slate-400 mt-1 leading-relaxed">
              Trojanized APK detection and remote-access software permission auditor (in development).
            </div>
          </div>
        </div>

        {/* Future Module: Network Sentinel */}
        <div className="p-4 rounded-2xl bg-surface border border-surface-border/70 space-y-3 opacity-60">
          <div className="flex items-center justify-between">
            <div className="p-2 rounded-xl bg-surface-elevated text-slate-400 border border-surface-border">
              <Shield className="w-5 h-5" />
            </div>
            <span className="flex items-center gap-1 text-[11px] font-medium text-slate-400 bg-surface-elevated px-2 py-0.5 rounded-full">
              <Clock className="w-3 h-3" />
              Roadmap
            </span>
          </div>
          <div>
            <div className="font-bold text-slate-300 text-sm">Network Sentinel</div>
            <div className="text-xs text-slate-400 mt-1 leading-relaxed">
              Home Wi-Fi router DNS hijacks and rogue hotspot protection (in development).
            </div>
          </div>
        </div>

      </div>
    </div>
  );
};
