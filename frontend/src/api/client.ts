import {
  HealthResponse,
  TextAnalysisRequest,
  TextAnalysisResponse,
  FamilyShareRequest,
  FamilyShareResponse,
  AudioAnalysisResponse
} from './types';

const API_BASE = import.meta.env.VITE_API_BASE_URL || '/api/v1';

export class ApiError extends Error {
  status: number;
  data: any;

  constructor(message: string, status: number, data?: any) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.data = data;
  }
}

async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    let errData: any;
    try {
      errData = await res.json();
    } catch {
      errData = { message: res.statusText };
    }

    const detailMsg =
      typeof errData?.detail === 'string'
        ? errData.detail
        : typeof errData?.detail?.message === 'string'
        ? errData.detail.message
        : Array.isArray(errData?.detail)
        ? errData.detail.map((d: any) => d.msg || JSON.stringify(d)).join('; ')
        : errData?.message || `Request failed with status ${res.status}`;

    throw new ApiError(detailMsg, res.status, errData);
  }
  return res.json() as Promise<T>;
}

export async function fetchHealth(): Promise<HealthResponse> {
  const res = await fetch(`${API_BASE}/health`, {
    headers: { 'Accept': 'application/json' }
  });
  return handleResponse<HealthResponse>(res);
}

export async function analyzeText(req: TextAnalysisRequest): Promise<TextAnalysisResponse> {
  const res = await fetch(`${API_BASE}/analyze/text`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json'
    },
    body: JSON.stringify(req)
  });
  return handleResponse<TextAnalysisResponse>(res);
}

export async function analyzeCallTranscript(text: string): Promise<TextAnalysisResponse> {
  const res = await fetch(`${API_BASE}/analyze/call/transcript`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json'
    },
    body: JSON.stringify({ text, input_type: 'call_transcript' })
  });
  return handleResponse<TextAnalysisResponse>(res);
}

export async function uploadCallAudio(file: File): Promise<AudioAnalysisResponse> {
  const formData = new FormData();
  formData.append('file', file);

  const res = await fetch(`${API_BASE}/analyze/call/audio`, {
    method: 'POST',
    headers: { 'Accept': 'application/json' },
    body: formData
  });
  return handleResponse<AudioAnalysisResponse>(res);
}

export async function fetchFamilyShareSummary(req: FamilyShareRequest): Promise<FamilyShareResponse> {
  const res = await fetch(`${API_BASE}/family/share-summary`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json'
    },
    body: JSON.stringify(req)
  });
  return handleResponse<FamilyShareResponse>(res);
}
