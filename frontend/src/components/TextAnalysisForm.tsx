import React, { useState } from 'react';
import { InputType, TextAnalysisResponse } from '../api/types';
import { useTextAnalysis } from '../hooks/useTextAnalysis';
import { ConsentNotice } from './ConsentNotice';
import { LoadingState } from './LoadingState';
import { ErrorState } from './ErrorState';
import { RiskResultCard } from './RiskResultCard';
import { PhoneCall, MessageSquare, Mail, CreditCard, Share2, Sparkles, Trash2, Shield } from 'lucide-react';

const PRESETS = [
  {
    title: '🚨 Digital Arrest Scam (Call)',
    type: 'call_transcript' as InputType,
    text: 'This is Inspector Sharma from Cyber Cell New Delhi. A seized courier contains illegal passports and narcotics linked to your Aadhaar card. You are placed under digital arrest. Stay on this video call, do not disconnect, and transfer verification funds immediately.'
  },
  {
    title: '⚡ Electricity Cutoff Threat (SMS)',
    type: 'sms' as InputType,
    text: 'Dear Customer, your electricity power will be disconnected tonight at 9:30 PM due to unpaid electricity bill. Contact electricity verification officer at 9876543210 immediately.'
  },
  {
    title: '💸 UPI PIN Cashback Trap (WhatsApp)',
    type: 'whatsapp' as InputType,
    text: 'Congratulations! You have received Rs 25,000 lottery cashback. Click to open UPI app, scan the dynamic QR code and enter your confidential 6-digit UPI PIN to credit reward.'
  },
  {
    title: '📱 Remote Support Coercion (Call)',
    type: 'call_transcript' as InputType,
    text: 'Hello sir, calling from bank technical support. Your account shows high risk security vulnerability. Please install RemoteAssistDemo app from Play Store and read out the 9-digit session code.'
  },
  {
    title: '✅ Legitimate Bank OTP Alert (Safe Contrast)',
    type: 'sms' as InputType,
    text: '123456 is your secret OTP for login to Example Bank NetBanking. Never share your OTP with anyone including bank staff or callers. OTP valid for 5 minutes.'
  }
];

export const TextAnalysisForm: React.FC = () => {
  const [text, setText] = useState('');
  const [inputType, setInputType] = useState<InputType>('call_transcript');
  const { runAnalysis, result, isLoading, error, reset } = useTextAnalysis();

  const nonWhitespaceLength = text.replace(/\s+/g, '').length;
  const isValidLength = nonWhitespaceLength >= 10;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!isValidLength || isLoading) return;
    try {
      await runAnalysis({ text, input_type: inputType });
    } catch {
      // Error handled by hook
    }
  };

  const handleClear = () => {
    setText('');
    reset();
  };

  const handleSelectPreset = (preset: typeof PRESETS[0]) => {
    setText(preset.text);
    setInputType(preset.type);
    reset();
  };

  const channelOptions: { value: InputType; label: string; icon: any }[] = [
    { value: 'call_transcript', label: 'Call Transcript', icon: PhoneCall },
    { value: 'sms', label: 'SMS Text', icon: MessageSquare },
    { value: 'whatsapp', label: 'WhatsApp', icon: MessageSquare },
    { value: 'email', label: 'Email', icon: Mail },
    { value: 'payment_message', label: 'Payment Request', icon: CreditCard },
    { value: 'social_message', label: 'Social Message', icon: Share2 },
  ];

  return (
    <div className="space-y-6">

      {/* Preset Scenarios Selector */}
      <div className="space-y-2">
        <div className="flex items-center gap-2 text-xs font-semibold text-slate-300">
          <Sparkles className="w-4 h-4 text-cyan-accent" />
          <span>Or load a common scam or legitimate sample to test:</span>
        </div>
        <div className="flex items-center gap-2 overflow-x-auto pb-2 scrollbar-none">
          {PRESETS.map((p, idx) => (
            <button
              key={idx}
              type="button"
              onClick={() => handleSelectPreset(p)}
              className="text-xs px-3 py-1.5 rounded-lg bg-surface border border-surface-border text-slate-300 hover:text-white hover:border-cyan-500/50 whitespace-nowrap transition-all"
            >
              {p.title}
            </button>
          ))}
        </div>
      </div>

      <form onSubmit={handleSubmit} className="p-6 sm:p-8 rounded-3xl glass-panel space-y-6">

        {/* Channel Selection Buttons */}
        <div className="space-y-2">
          <label className="block text-xs font-semibold uppercase tracking-wider text-slate-400">
            1. Select Communication Vector
          </label>
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-2">
            {channelOptions.map((opt) => {
              const Icon = opt.icon;
              const isSelected = inputType === opt.value;
              return (
                <button
                  key={opt.value}
                  type="button"
                  onClick={() => setInputType(opt.value)}
                  className={`flex flex-col items-center justify-center p-3 rounded-xl border text-xs font-medium transition-all ${
                    isSelected
                      ? 'bg-cyan-950/80 text-cyan-300 border-cyan-500 shadow-md shadow-cyan-950/50'
                      : 'bg-surface border-surface-border text-slate-300 hover:bg-surface-elevated'
                  }`}
                >
                  <Icon className="w-4 h-4 mb-1.5" />
                  <span className="text-center">{opt.label}</span>
                </button>
              );
            })}
          </div>
        </div>

        {/* Text Area Input */}
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <label htmlFor="message-text" className="text-xs font-semibold uppercase tracking-wider text-slate-400">
              2. Paste or Type Message / Transcript
            </label>
            <span className={`text-xs font-mono ${nonWhitespaceLength >= 10 ? 'text-cyan-400' : 'text-slate-500'}`}>
              {nonWhitespaceLength} / 10 min chars
            </span>
          </div>

          <textarea
            id="message-text"
            rows={5}
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="Paste what the caller said, an SMS, WhatsApp message, or payment notification here..."
            className="w-full p-4 rounded-2xl bg-surface-elevated border border-surface-border text-slate-100 placeholder-slate-500 text-sm focus:outline-none focus:ring-2 focus:ring-cyan-500/50 focus:border-cyan-500 transition-all font-sans leading-relaxed"
          />
        </div>

        {/* Mandatory Privacy Reminder */}
        <ConsentNotice type="text" />

        {/* Actions */}
        <div className="flex flex-col sm:flex-row items-center justify-between gap-3 pt-2">
          {text && (
            <button
              type="button"
              onClick={handleClear}
              className="w-full sm:w-auto px-4 py-2.5 rounded-xl bg-surface hover:bg-surface-elevated border border-surface-border text-slate-400 hover:text-white text-xs font-medium flex items-center justify-center gap-1.5 transition-colors"
            >
              <Trash2 className="w-4 h-4" />
              <span>Clear Text</span>
            </button>
          )}

          <button
            type="submit"
            disabled={!isValidLength || isLoading}
            className="w-full sm:w-auto sm:ml-auto px-8 py-3.5 rounded-xl bg-cyan-600 hover:bg-cyan-500 disabled:opacity-50 text-white font-bold text-sm sm:text-base flex items-center justify-center gap-2 transition-all shadow-lg shadow-cyan-950/60"
          >
            <Shield className="w-5 h-5 text-white" />
            <span>Analyze with SentryMesh V4</span>
          </button>
        </div>

      </form>

      {/* Loading & Error States */}
      {isLoading && <LoadingState />}
      {error && <ErrorState message={error} onRetry={() => runAnalysis({ text, input_type: inputType })} />}

      {/* Analysis Result */}
      {result && <RiskResultCard result={result} />}

    </div>
  );
};
