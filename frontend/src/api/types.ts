export type InputType =
  | 'call_transcript'
  | 'sms'
  | 'whatsapp'
  | 'email'
  | 'payment_message'
  | 'social_message';

export type PredictedLabel = 'suspicious' | 'legitimate';

export type SafetyLevel =
  | 'high_risk'
  | 'suspicious_needs_verification'
  | 'uncertain_needs_verification'
  | 'no_strong_risk_signal';

export interface HealthResponse {
  status: string;
  model_loaded: boolean;
  model_name: string;
  selected_suspicious_threshold: number;
  audio_transcription_configured: boolean;
  voice_authenticity_configured: boolean;
}

export interface TextAnalysisRequest {
  text: string;
  input_type: InputType;
}

export interface EvidenceItem {
  feature: string;
  contribution: number;
}

export interface ModelEvidence {
  signals_favoring_suspicious: EvidenceItem[];
  signals_favoring_legitimate: EvidenceItem[];
}

export interface ExplanationBlock {
  summary: string;
  evidence_summary: string[];
  uncertainty_note: string;
}

export interface TextAnalysisResponse {
  module: string;
  status: string;
  predicted_label: PredictedLabel;
  suspicious_probability: number;
  selected_threshold: number;
  safety_level: SafetyLevel;
  input_type: InputType;
  model_evidence: ModelEvidence;
  explanation: ExplanationBlock;
  recommended_actions: string[];
  privacy_notice: string;
  disclaimer: string;
}

export interface FamilyShareRequest {
  safety_level: SafetyLevel;
  suspicious_probability: number;
  evidence_summary: string[];
  recommended_actions: string[];
  disclaimer?: string;
}

export interface FamilyShareResponse {
  title: string;
  safety_level: SafetyLevel;
  safety_level_display: string;
  why_text: string;
  recommended_action_text: string;
  disclaimer_text: string;
  full_share_text: string;
}

export interface AudioNotConfiguredResponse {
  module: string;
  status: 'not_configured';
  message: string;
}

export interface AudioAnalysisResponse {
  module: string;
  status: string;
  transcription_analysis?: TextAnalysisResponse;
  voice_authenticity_analysis?: {
    module: string;
    status: string;
    message: string;
  };
}
