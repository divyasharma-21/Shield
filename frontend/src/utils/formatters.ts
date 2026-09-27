/**
 * Data formatters for ParentCall Guardian.
 */

export function formatProbabilityPercent(prob: number): string {
  if (typeof prob !== 'number' || isNaN(prob)) return '0.0%';
  return `${(prob * 100).toFixed(1)}%`;
}

export function formatContribution(val: number): string {
  if (typeof val !== 'number' || isNaN(val)) return '0.000';
  const prefix = val > 0 ? '+' : '';
  return `${prefix}${val.toFixed(3)}`;
}

export function formatInputTypeLabel(type: string): string {
  const map: Record<string, string> = {
    call_transcript: 'Call Transcript',
    sms: 'SMS Message',
    whatsapp: 'WhatsApp Message',
    email: 'Email',
    payment_message: 'Payment Communication',
    social_message: 'Social Media Message'
  };
  return map[type] || type.replace('_', ' ').toUpperCase();
}
