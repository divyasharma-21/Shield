import React, { useState, useRef } from 'react';
import { UploadCloud, Music, ShieldAlert, CheckCircle, Trash2, Cpu } from 'lucide-react';
import { useAudioAnalysis } from '../hooks/useAudioAnalysis';
import { ConsentNotice } from './ConsentNotice';
import { LoadingState } from './LoadingState';
import { ErrorState } from './ErrorState';
import { RiskResultCard } from './RiskResultCard';

const SUPPORTED_FORMATS = ['.wav', '.mp3', '.m4a', '.webm'];
const MAX_FILE_SIZE_MB = 20;

export const AudioUploadForm: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [hasConsented, setHasConsented] = useState<boolean>(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const { uploadAudio, result, isLoading, error, unconfiguredMessage, reset } = useAudioAnalysis();

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selected = e.target.files[0];
      if (selected.size > MAX_FILE_SIZE_MB * 1024 * 1024) {
        alert(`File exceeds maximum size of ${MAX_FILE_SIZE_MB}MB.`);
        return;
      }
      setFile(selected);
      reset();
    }
  };

  const handleClear = () => {
    setFile(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
    reset();
  };

  const handleUploadSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file || !hasConsented || isLoading) return;
    try {
      await uploadAudio(file);
    } catch {
      // Handled in hook
    }
  };

  return (
    <div className="space-y-6">

      {/* 1. Explicit Consent Notice First */}
      <ConsentNotice type="audio" />

      <form onSubmit={handleUploadSubmit} className="p-6 sm:p-8 rounded-3xl glass-panel space-y-6">

        {/* User Consent Checkbox */}
        <div className="p-4 rounded-xl bg-surface border border-surface-border">
          <label className="flex items-start gap-3 cursor-pointer text-xs sm:text-sm text-slate-300">
            <input
              type="checkbox"
              checked={hasConsented}
              onChange={(e) => setHasConsented(e.target.checked)}
              className="mt-0.5 w-4 h-4 rounded text-cyan-600 focus:ring-cyan-500 bg-surface-elevated border-surface-border cursor-pointer"
            />
            <span>
              I voluntarily choose to upload this call recording for in-memory risk inspection.
              I understand SentryMesh will process it temporarily and delete it immediately.
            </span>
          </label>
        </div>

        {/* Audio File Picker Area */}
        <div className="space-y-2">
          <input
            ref={fileInputRef}
            type="file"
            accept={SUPPORTED_FORMATS.join(',')}
            disabled={!hasConsented || isLoading}
            onChange={handleFileChange}
            className="hidden"
            id="audio-file-upload"
          />

          {!file ? (
            <label
              htmlFor="audio-file-upload"
              className={`border-2 border-dashed rounded-2xl p-8 flex flex-col items-center justify-center text-center cursor-pointer transition-all ${
                hasConsented
                  ? 'border-surface-border hover:border-cyan-500/60 bg-surface-elevated/40 hover:bg-surface-elevated/70'
                  : 'border-surface-border/40 opacity-50 cursor-not-allowed bg-surface/40'
              }`}
            >
              <UploadCloud className="w-10 h-10 text-cyan-accent mb-3 animate-bounce" />
              <div className="font-semibold text-white text-sm">
                Click to select a voluntary audio recording
              </div>
              <p className="text-xs text-slate-400 mt-1">
                Supported formats: {SUPPORTED_FORMATS.join(', ')} • Max size: {MAX_FILE_SIZE_MB}MB
              </p>
            </label>
          ) : (
            <div className="p-4 rounded-xl bg-surface border border-cyan-500/30 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="p-2.5 rounded-lg bg-cyan-950 text-cyan-400 border border-cyan-800">
                  <Music className="w-5 h-5" />
                </div>
                <div>
                  <div className="font-medium text-white text-sm truncate max-w-xs sm:max-w-md">
                    {file.name}
                  </div>
                  <div className="text-xs text-slate-400">
                    {(file.size / (1024 * 1024)).toFixed(2)} MB
                  </div>
                </div>
              </div>
              <button
                type="button"
                onClick={handleClear}
                className="p-2 text-slate-400 hover:text-red-400 hover:bg-surface-elevated rounded-lg transition-colors"
                title="Remove audio file"
              >
                <Trash2 className="w-4 h-4" />
              </button>
            </div>
          )}
        </div>

        {/* Action Button */}
        <div className="flex justify-end pt-2">
          <button
            type="submit"
            disabled={!file || !hasConsented || isLoading}
            className="w-full sm:w-auto px-8 py-3.5 rounded-xl bg-cyan-600 hover:bg-cyan-500 disabled:opacity-50 text-white font-bold text-sm sm:text-base flex items-center justify-center gap-2 transition-all shadow-lg shadow-cyan-950/60"
          >
            <Cpu className="w-5 h-5 text-white" />
            <span>Process & Inspect Recording</span>
          </button>
        </div>

      </form>

      {/* Loading State */}
      {isLoading && (
        <LoadingState message="Transcribing audio via local speech-to-text and assessing fraud patterns..." />
      )}

      {/* Honest Unconfigured Module Feedback */}
      {unconfiguredMessage && (
        <div className="p-6 rounded-2xl glass-panel border border-amber-500/40 space-y-3">
          <div className="flex items-center gap-2 text-amber-400 font-bold text-sm">
            <ShieldAlert className="w-5 h-5 shrink-0" />
            <span>Audio Transcription Service Unconfigured</span>
          </div>
          <p className="text-xs sm:text-sm text-slate-300 leading-relaxed font-sans">
            {unconfiguredMessage}
          </p>
          <div className="p-3 rounded-lg bg-surface border border-surface-border text-xs text-slate-400 space-y-1">
            <span className="font-semibold text-slate-300">Why are you seeing this?</span>
            <p>
              In accordance with SentryMesh's strict integrity standards, we <strong>never generate fake transcripts or unverified deepfake scores</strong>.
              To analyze audio files, configure a local speech-to-text pipeline (such as <code>faster-whisper</code>) and enable <code>ENABLE_AUDIO_TRANSCRIPTION=true</code>.
            </p>
          </div>
          <div className="pt-2 text-xs text-cyan-300 font-medium">
            💡 Quick Tip: You can type or paste what the caller said into the <strong>"Type or paste call details"</strong> tab to analyze it immediately with the active V4 model!
          </div>
        </div>
      )}

      {/* Generic Error */}
      {error && !unconfiguredMessage && (
        <ErrorState message={error} onRetry={() => file && uploadAudio(file)} />
      )}

      {/* Successful Transcription & Analysis */}
      {result?.transcription_analysis && (
        <div className="space-y-4">
          <div className="p-4 rounded-xl bg-cyan-950/40 border border-cyan-500/30 flex items-center gap-2 text-xs text-cyan-300 font-semibold">
            <CheckCircle className="w-4 h-4 text-cyan-400" />
            <span>Audio successfully transcribed and evaluated with SentryMesh V4!</span>
          </div>
          <RiskResultCard result={result.transcription_analysis} />
        </div>
      )}

    </div>
  );
};
