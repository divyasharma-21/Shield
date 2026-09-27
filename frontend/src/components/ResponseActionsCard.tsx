import React from 'react';
import { Ban, CheckCircle, PhoneCall, AlertTriangle, ShieldCheck } from 'lucide-react';

export const ResponseActionsCard: React.FC = () => {
  return (
    <div className="space-y-6">

      {/* Golden Rule Banner */}
      <div className="p-4 sm:p-5 rounded-2xl bg-gradient-to-r from-cyan-950/80 via-slate-900 to-cyan-950/80 border border-cyan-500/40 text-center space-y-1">
        <span className="text-xs uppercase tracking-widest text-cyan-400 font-bold">Universal Golden Rule</span>
        <h3 className="text-xl sm:text-2xl font-extrabold text-white tracking-tight">Pause. Verify. Protect.</h3>
        <p className="text-xs sm:text-sm text-slate-300 max-w-xl mx-auto">
          Scammers depend on fear, urgency, and isolation. Taking 5 minutes to pause and independently check breaks their psychological control.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">

        {/* DO NOT Column */}
        <div className="p-6 rounded-2xl glass-panel border border-red-500/30 space-y-4">
          <div className="flex items-center gap-2.5 text-red-400 pb-3 border-b border-surface-border">
            <Ban className="w-5 h-5 shrink-0" />
            <h4 className="font-bold text-white text-base">Under Pressure — DO NOT:</h4>
          </div>

          <ul className="space-y-2.5 text-xs sm:text-sm text-slate-200">
            <li className="flex items-start gap-2">
              <span className="text-red-400 font-bold shrink-0">✕</span>
              <span><strong>Send money or penalty fees:</strong> No legitimate police, CBI, customs, or court settles cases over Skype, WhatsApp, or phone calls.</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-red-400 font-bold shrink-0">✕</span>
              <span><strong>Share OTPs or passwords:</strong> Bank staff and genuine support will never request your one-time passwords.</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-red-400 font-bold shrink-0">✕</span>
              <span><strong>Enter your UPI PIN to receive money:</strong> Entering a PIN <em>always</em> transfers money out of your account.</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-red-400 font-bold shrink-0">✕</span>
              <span><strong>Install remote-support apps:</strong> Never download AnyDesk, TeamViewer, or QuickSupport at the request of an incoming caller.</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-red-400 font-bold shrink-0">✕</span>
              <span><strong>Share your screen:</strong> Screen sharing allows attackers to capture incoming SMS codes and NetBanking passwords silently.</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-red-400 font-bold shrink-0">✕</span>
              <span><strong>Enable Accessibility permissions:</strong> Fake bank apps demand Accessibility to bypass PIN and security locks.</span>
            </li>
          </ul>
        </div>

        {/* VERIFY Column */}
        <div className="p-6 rounded-2xl glass-panel border border-emerald-500/30 space-y-4">
          <div className="flex items-center gap-2.5 text-emerald-400 pb-3 border-b border-surface-border">
            <CheckCircle className="w-5 h-5 shrink-0" />
            <h4 className="font-bold text-white text-base">Safely Verify Independently:</h4>
          </div>

          <ul className="space-y-2.5 text-xs sm:text-sm text-slate-200">
            <li className="flex items-start gap-2">
              <span className="text-emerald-400 font-bold shrink-0">✓</span>
              <span><strong>Use the official mobile app:</strong> Open your bank or utility app directly from your phone rather than following links in messages.</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-emerald-400 font-bold shrink-0">✓</span>
              <span><strong>Call published numbers:</strong> Use the contact number printed on the back of your debit card or the official company website.</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-emerald-400 font-bold shrink-0">✓</span>
              <span><strong>Never dial numbers supplied by the caller:</strong> Fraudulent SMS and calls provide fake "helpline" numbers that connect back to accomplice rings.</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-emerald-400 font-bold shrink-0">✓</span>
              <span><strong>Consult a trusted family member:</strong> Discuss unexpected emergencies with a loved one before making wire transfers or payments.</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-emerald-400 font-bold shrink-0">✓</span>
              <span><strong>Visit the local branch or office:</strong> For high-stakes threats (power cut, digital arrest, frozen account), visit the physical branch in daylight.</span>
            </li>
          </ul>
        </div>

      </div>

      {/* Emergency Escalation */}
      <div className="p-6 rounded-2xl bg-surface-elevated border border-cyan-500/40 space-y-4">
        <div className="flex items-center gap-2 text-cyan-300 font-bold text-base">
          <PhoneCall className="w-5 h-5 text-cyan-accent" />
          <span>If Money Was Already Sent or Compromised</span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-xs sm:text-sm">
          <div className="p-4 rounded-xl bg-surface border border-surface-border space-y-1.5">
            <div className="font-semibold text-white">1. Contact Bank Immediately</div>
            <p className="text-slate-300 text-xs">
              Call your bank's fraud line immediately to freeze accounts, debit cards, and dispute unauthorized UPI transactions.
            </p>
          </div>
          <div className="p-4 rounded-xl bg-surface border border-surface-border space-y-1.5">
            <div className="font-semibold text-white">2. National Helpline 1930</div>
            <p className="text-slate-300 text-xs">
              In India, dial <strong>1930</strong> (Citizen Financial Cyber Fraud Reporting System) to trigger swift transaction freeze protocols.
            </p>
          </div>
          <div className="p-4 rounded-xl bg-surface border border-surface-border space-y-1.5">
            <div className="font-semibold text-white">3. Preserve All Evidence</div>
            <p className="text-slate-300 text-xs">
              Save screenshots, UPI transaction IDs, phone numbers, WhatsApp chats, and call logs. Report on <span className="text-cyan-400 font-mono">cybercrime.gov.in</span>.
            </p>
          </div>
        </div>

        <p className="text-[11px] text-slate-500 italic">
          *Note: Reporting numbers and procedures may vary by state and jurisdiction. For assistance outside India, contact your national cybercrime agency and local banking ombudsman.
        </p>
      </div>

    </div>
  );
};
