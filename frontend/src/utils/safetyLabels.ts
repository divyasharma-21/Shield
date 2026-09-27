import { SafetyLevel } from '../api/types';

export interface SafetyLevelMeta {
  title: string;
  badgeText: string;
  parentLabel: string;
  description: string;
  colorClass: string;
  borderClass: string;
  bgClass: string;
  glowClass: string;
  iconName: 'AlertOctagon' | 'AlertTriangle' | 'HelpCircle' | 'ShieldCheck';
}

export const SAFETY_LEVEL_MAP: Record<SafetyLevel, SafetyLevelMeta> = {
  high_risk: {
    title: 'High Risk Threat',
    badgeText: 'HIGH RISK',
    parentLabel: 'Stop. Do not send money or share credentials.',
    description: 'The language in this communication strongly matches patterns commonly seen in financial fraud, authority impersonation, or credential theft.',
    colorClass: 'text-red-400',
    borderClass: 'border-red-500/50',
    bgClass: 'bg-red-950/40',
    glowClass: 'glow-risk-high',
    iconName: 'AlertOctagon'
  },
  suspicious_needs_verification: {
    title: 'Suspicious — Needs Verification',
    badgeText: 'SUSPICIOUS',
    parentLabel: 'Pause and verify before responding.',
    description: 'The message shows indicators of potential risk or coercion. Treat requests for money, OTPs, or remote access with caution.',
    colorClass: 'text-amber-400',
    borderClass: 'border-amber-500/50',
    bgClass: 'bg-amber-950/40',
    glowClass: 'glow-risk-suspicious',
    iconName: 'AlertTriangle'
  },
  uncertain_needs_verification: {
    title: 'Uncertain — Verification Required',
    badgeText: 'UNCERTAIN',
    parentLabel: 'Uncertain signal. Do not trust without verification.',
    description: 'The text cannot be confidently assessed from text patterns alone. Treat requests for money, passwords, or screen sharing as high risk until verified.',
    colorClass: 'text-violet-300',
    borderClass: 'border-violet-500/50',
    bgClass: 'bg-violet-950/40',
    glowClass: 'glow-risk-uncertain',
    iconName: 'HelpCircle'
  },
  no_strong_risk_signal: {
    title: 'No Strong Risk Signal Found',
    badgeText: 'LOW TEXT SIGNAL',
    parentLabel: 'No strong scam signal detected in this text.',
    description: 'No dominant scam indicators were detected from this text. However, this is never a guarantee of safety. Always verify unexpected financial requests.',
    colorClass: 'text-emerald-400',
    borderClass: 'border-emerald-500/50',
    bgClass: 'bg-emerald-950/40',
    glowClass: 'glow-risk-low',
    iconName: 'ShieldCheck'
  }
};

export function getSafetyMeta(level: SafetyLevel): SafetyLevelMeta {
  return SAFETY_LEVEL_MAP[level] || SAFETY_LEVEL_MAP.uncertain_needs_verification;
}
