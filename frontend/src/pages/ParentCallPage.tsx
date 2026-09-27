import React, { useState } from 'react';
import { PhoneCall, UploadCloud, MessageSquare, Shield, HelpCircle } from 'lucide-react';
import { TextAnalysisForm } from '../components/TextAnalysisForm';
import { AudioUploadForm } from '../components/AudioUploadForm';

export const ParentCallPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'call_text' | 'audio' | 'message'>('call_text');

  return (
    <div className="max-w-5xl mx-auto py-6 sm:py-10 px-4 space-y-8">

      {/* Header section */}
      <div className="space-y-2 text-center sm:text-left">
        <div className="flex items-center justify-center sm:justify-start gap-2 text-cyan-400 font-semibold text-xs sm:text-sm tracking-wide uppercase">
          <Shield className="w-4 h-4 text-cyan-accent" />
          <span>ParentCall Guardian Module</span>
        </div>
        <h1 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight">
          ParentCall Guardian
        </h1>
        <p className="text-sm sm:text-base text-slate-300 max-w-3xl leading-relaxed">
          Paste what a caller said, type important details from a call, or upload a recording you choose to share.
          SentryMesh evaluates patterns against our real V4 binary model to provide calm, objective safety guidance.
        </p>
      </div>

      {/* Tabs */}
      <div className="flex items-center gap-2 border-b border-surface-border overflow-x-auto pb-px">
        <button
          onClick={() => setActiveTab('call_text')}
          className={`flex items-center gap-2 py-3 px-4 font-semibold text-xs sm:text-sm rounded-t-xl transition-all border-b-2 whitespace-nowrap ${
            activeTab === 'call_text'
              ? 'border-cyan-400 text-cyan-300 bg-surface'
              : 'border-transparent text-slate-400 hover:text-slate-200 hover:bg-surface/50'
          }`}
        >
          <PhoneCall className="w-4 h-4" />
          <span>1. Type or paste call details</span>
        </button>

        <button
          onClick={() => setActiveTab('audio')}
          className={`flex items-center gap-2 py-3 px-4 font-semibold text-xs sm:text-sm rounded-t-xl transition-all border-b-2 whitespace-nowrap ${
            activeTab === 'audio'
              ? 'border-cyan-400 text-cyan-300 bg-surface'
              : 'border-transparent text-slate-400 hover:text-slate-200 hover:bg-surface/50'
          }`}
        >
          <UploadCloud className="w-4 h-4" />
          <span>2. Upload a recording</span>
        </button>

        <button
          onClick={() => setActiveTab('message')}
          className={`flex items-center gap-2 py-3 px-4 font-semibold text-xs sm:text-sm rounded-t-xl transition-all border-b-2 whitespace-nowrap ${
            activeTab === 'message'
              ? 'border-cyan-400 text-cyan-300 bg-surface'
              : 'border-transparent text-slate-400 hover:text-slate-200 hover:bg-surface/50'
          }`}
        >
          <MessageSquare className="w-4 h-4" />
          <span>3. Check a suspicious message</span>
        </button>
      </div>

      {/* Tab Panels */}
      <div className="pt-2">
        {activeTab === 'call_text' && (
          <div className="space-y-4">
            <div className="p-3 rounded-xl bg-surface text-xs text-slate-400 flex items-center gap-2">
              <HelpCircle className="w-4 h-4 text-cyan-accent shrink-0" />
              <span>
                Tip: Enter what the caller claimed (e.g. police/CBI, bank manager, customs, parcel seizure, or netbanking security alert).
              </span>
            </div>
            <TextAnalysisForm />
          </div>
        )}

        {activeTab === 'audio' && (
          <div className="space-y-4">
            <AudioUploadForm />
          </div>
        )}

        {activeTab === 'message' && (
          <div className="space-y-4">
            <div className="p-3 rounded-xl bg-surface text-xs text-slate-400 flex items-center gap-2">
              <HelpCircle className="w-4 h-4 text-cyan-accent shrink-0" />
              <span>
                Tip: Check SMS notifications, WhatsApp forward threats, suspicious lottery announcements, or payment links.
              </span>
            </div>
            <TextAnalysisForm />
          </div>
        )}
      </div>

    </div>
  );
};
