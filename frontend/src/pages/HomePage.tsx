import React from 'react';
import { Link } from 'react-router-dom';
import { PhoneCall, MessageSquare, AlertTriangle, ShieldCheck, Lock, ArrowRight, Radio } from 'lucide-react';
import { ModuleStatusCard } from '../components/ModuleStatusCard';
import { useHealth } from '../hooks/useHealth';

export const HomePage: React.FC = () => {
  const { data: health } = useHealth();

  return (
    <div className="space-y-12 sm:space-y-16 py-6 sm:py-10">

      {/* Hero Section */}
      <section className="text-center max-w-4xl mx-auto space-y-6 sm:space-y-8 px-4">

        {/* Model status pill */}
        <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-surface border border-cyan-500/40 text-xs sm:text-sm font-medium text-cyan-300 shadow-lg shadow-cyan-950/40">
          <Radio className="w-3.5 h-3.5 text-cyan-accent animate-pulse" />
          <span>Real SentryMesh V4 Binary Fraud Model</span>
          <span className="text-slate-500">•</span>
          <span className="font-mono text-cyan-light">Threshold: {health?.selected_suspicious_threshold ?? '0.40'}</span>
        </div>

        {/* Hero Title & Tagline */}
        <div className="space-y-3 sm:space-y-4">
          <h1 className="text-4xl sm:text-6xl lg:text-7xl font-extrabold tracking-tight text-white leading-tight">
            SentryMesh <span className="bg-gradient-to-r from-cyan-400 via-sky-300 to-cyan-500 bg-clip-text text-transparent">Guardian</span>
          </h1>
          <p className="text-xl sm:text-3xl font-bold text-cyan-300 tracking-wide">
            Pause. Verify. Protect.
          </p>
        </div>

        {/* Subheading */}
        <p className="text-base sm:text-xl text-slate-300 max-w-2xl mx-auto leading-relaxed">
          A privacy-first scam shield that helps families understand suspicious calls, messages, and payment requests before they act.
        </p>

        {/* Primary CTA */}
        <div className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-2">
          <Link
            to="/parent-call"
            className="w-full sm:w-auto px-8 py-4 rounded-2xl bg-cyan-600 hover:bg-cyan-500 text-white font-bold text-base sm:text-lg flex items-center justify-center gap-3 transition-all shadow-xl shadow-cyan-950/70 hover:scale-[1.02] active:scale-[0.98]"
          >
            <PhoneCall className="w-5 h-5 text-white" />
            <span>I received a suspicious call</span>
            <ArrowRight className="w-5 h-5" />
          </Link>
          <Link
            to="/response"
            className="w-full sm:w-auto px-6 py-4 rounded-2xl bg-surface hover:bg-surface-elevated border border-surface-border text-slate-200 hover:text-white font-semibold text-base flex items-center justify-center gap-2 transition-colors"
          >
            <AlertTriangle className="w-5 h-5 text-amber-400" />
            <span>Emergency Checklist</span>
          </Link>
        </div>

        {/* Privacy Banner */}
        <div className="p-4 rounded-2xl bg-surface/60 border border-surface-border text-xs sm:text-sm text-slate-400 max-w-2xl mx-auto flex items-center justify-center gap-2">
          <Lock className="w-4 h-4 text-cyan-accent shrink-0" />
          <span>
            <strong>Privacy Guarantee:</strong> SentryMesh analyzes only information you choose to submit. It does not record calls, read private chats, or access banking information.
          </span>
        </div>

      </section>

      {/* Secondary Quick Action Cards */}
      <section className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-6xl mx-auto px-4">

        {/* Card 1: Check a suspicious message */}
        <Link
          to="/parent-call"
          className="p-6 sm:p-8 rounded-3xl glass-panel border border-surface-border hover:border-cyan-500/50 hover:bg-surface-elevated/70 transition-all group flex flex-col justify-between space-y-4"
        >
          <div className="space-y-3">
            <div className="w-12 h-12 rounded-2xl bg-cyan-950 border border-cyan-800 text-cyan-400 flex items-center justify-center group-hover:scale-110 transition-transform">
              <MessageSquare className="w-6 h-6" />
            </div>
            <h3 className="text-lg font-bold text-white group-hover:text-cyan-light transition-colors">
              Check a suspicious message
            </h3>
            <p className="text-xs sm:text-sm text-slate-300 leading-relaxed">
              Paste SMS alerts, WhatsApp lottery texts, fake electricity disconnection notices, or unexpected payment refund requests.
            </p>
          </div>
          <div className="flex items-center gap-2 text-cyan-400 text-xs font-semibold pt-2">
            <span>Analyze text message</span>
            <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
          </div>
        </Link>

        {/* Card 2: How to respond safely */}
        <Link
          to="/response"
          className="p-6 sm:p-8 rounded-3xl glass-panel border border-surface-border hover:border-amber-500/50 hover:bg-surface-elevated/70 transition-all group flex flex-col justify-between space-y-4"
        >
          <div className="space-y-3">
            <div className="w-12 h-12 rounded-2xl bg-amber-950 border border-amber-800 text-amber-400 flex items-center justify-center group-hover:scale-110 transition-transform">
              <ShieldCheck className="w-6 h-6" />
            </div>
            <h3 className="text-lg font-bold text-white group-hover:text-amber-300 transition-colors">
              How to respond safely
            </h3>
            <p className="text-xs sm:text-sm text-slate-300 leading-relaxed">
              Step-by-step guidance on what to do when pressured: never enter UPI PINs, how to verify with banks, and helpline 1930 contacts.
            </p>
          </div>
          <div className="flex items-center gap-2 text-amber-400 text-xs font-semibold pt-2">
            <span>Read safety playbook</span>
            <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
          </div>
        </Link>

        {/* Card 3: Privacy and safety */}
        <Link
          to="/privacy"
          className="p-6 sm:p-8 rounded-3xl glass-panel border border-surface-border hover:border-violet-500/50 hover:bg-surface-elevated/70 transition-all group flex flex-col justify-between space-y-4"
        >
          <div className="space-y-3">
            <div className="w-12 h-12 rounded-2xl bg-violet-950 border border-violet-800 text-violet-400 flex items-center justify-center group-hover:scale-110 transition-transform">
              <Lock className="w-6 h-6" />
            </div>
            <h3 className="text-lg font-bold text-white group-hover:text-violet-300 transition-colors">
              Privacy and safety
            </h3>
            <p className="text-xs sm:text-sm text-slate-300 leading-relaxed">
              Transparent review of our zero-background-listening architecture, temporary in-memory processing, and model boundaries.
            </p>
          </div>
          <div className="flex items-center gap-2 text-violet-400 text-xs font-semibold pt-2">
            <span>View privacy promises</span>
            <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
          </div>
        </Link>

      </section>

      {/* Module Status Architecture */}
      <section className="max-w-6xl mx-auto px-4">
        <ModuleStatusCard />
      </section>

    </div>
  );
};
