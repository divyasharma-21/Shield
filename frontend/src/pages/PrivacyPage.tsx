import React from 'react';
import { Lock, ShieldCheck, EyeOff, Trash2, Users, AlertCircle, PhoneOff, DatabaseZap } from 'lucide-react';
import { Disclaimer } from '../components/Disclaimer';

export const PrivacyPage: React.FC = () => {
  return (
    <div className="max-w-4xl mx-auto py-6 sm:py-10 px-4 space-y-8">

      {/* Title */}
      <div className="space-y-2 text-center sm:text-left">
        <div className="flex items-center justify-center sm:justify-start gap-2 text-cyan-400 font-semibold text-xs sm:text-sm tracking-wide uppercase">
          <Lock className="w-4 h-4 text-cyan-accent" />
          <span>Transparency & Data Architecture</span>
        </div>
        <h1 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight">
          Privacy and Safety Commitments
        </h1>
        <p className="text-sm sm:text-base text-slate-300 max-w-3xl leading-relaxed">
          SentryMesh is engineered from the ground up as a privacy-preserving situational awareness tool.
          We believe scam protection should never require surrendering your personal privacy.
        </p>
      </div>

      {/* Commitments Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 sm:gap-6">

        <div className="p-6 rounded-2xl glass-panel space-y-3">
          <div className="w-10 h-10 rounded-xl bg-cyan-950 border border-cyan-800 text-cyan-400 flex items-center justify-center">
            <PhoneOff className="w-5 h-5" />
          </div>
          <h3 className="font-bold text-white text-base">No Background Call Recording</h3>
          <p className="text-xs sm:text-sm text-slate-300 leading-relaxed">
            SentryMesh never records your incoming or outgoing calls in the background. It never hooks into the device dialer or intercepts phone traffic.
          </p>
        </div>

        <div className="p-6 rounded-2xl glass-panel space-y-3">
          <div className="w-10 h-10 rounded-xl bg-cyan-950 border border-cyan-800 text-cyan-400 flex items-center justify-center">
            <EyeOff className="w-5 h-5" />
          </div>
          <h3 className="font-bold text-white text-base">No Private-Chat Scraping</h3>
          <p className="text-xs sm:text-sm text-slate-300 leading-relaxed">
            We never access WhatsApp, SMS databases, or email inboxes automatically. Analysis occurs only when you manually type or paste text into the inspector.
          </p>
        </div>

        <div className="p-6 rounded-2xl glass-panel space-y-3">
          <div className="w-10 h-10 rounded-xl bg-cyan-950 border border-cyan-800 text-cyan-400 flex items-center justify-center">
            <DatabaseZap className="w-5 h-5" />
          </div>
          <h3 className="font-bold text-white text-base">Zero Banking Access</h3>
          <p className="text-xs sm:text-sm text-slate-300 leading-relaxed">
            SentryMesh never connects to banking APIs, card accounts, or UPI apps. We never collect or store OTPs, UPI PINs, passwords, or CVVs.
          </p>
        </div>

        <div className="p-6 rounded-2xl glass-panel space-y-3">
          <div className="w-10 h-10 rounded-xl bg-cyan-950 border border-cyan-800 text-cyan-400 flex items-center justify-center">
            <Trash2 className="w-5 h-5" />
          </div>
          <h3 className="font-bold text-white text-base">In-Memory Audio Processing</h3>
          <p className="text-xs sm:text-sm text-slate-300 leading-relaxed">
            Voluntarily uploaded audio files are saved in secure temporary system files and permanently unlinked and deleted immediately after processing.
          </p>
        </div>

        <div className="p-6 rounded-2xl glass-panel space-y-3">
          <div className="w-10 h-10 rounded-xl bg-cyan-950 border border-cyan-800 text-cyan-400 flex items-center justify-center">
            <Users className="w-5 h-5" />
          </div>
          <h3 className="font-bold text-white text-base">Explicit Family Sharing</h3>
          <p className="text-xs sm:text-sm text-slate-300 leading-relaxed">
            Family verification summaries are shared exclusively when you click the Share button. We never access contacts or send unsolicited notifications.
          </p>
        </div>

        <div className="p-6 rounded-2xl glass-panel space-y-3">
          <div className="w-10 h-10 rounded-xl bg-cyan-950 border border-cyan-800 text-cyan-400 flex items-center justify-center">
            <AlertCircle className="w-5 h-5 text-amber-400" />
          </div>
          <h3 className="font-bold text-white text-base">Honest Technical Limitations</h3>
          <p className="text-xs sm:text-sm text-slate-300 leading-relaxed">
            A text-based AI model cannot prove caller identity or confirm deepfake audio. Voice-authenticity analysis remains disabled until a validated anti-spoof model is configured.
          </p>
        </div>

      </div>

      {/* Advisory Note */}
      <div className="p-6 rounded-2xl bg-surface border border-surface-border space-y-3">
        <h4 className="font-bold text-white text-sm">Best Practices When Submitting Text</h4>
        <p className="text-xs sm:text-sm text-slate-300 leading-relaxed">
          To protect your own privacy, avoid submitting unnecessary personal information such as your full home address, Aadhaar number, or PAN card number. You can replace real names with placeholders like [Name] or [City] before analyzing.
        </p>
      </div>

      {/* Disclaimer */}
      <Disclaimer />

    </div>
  );
};
