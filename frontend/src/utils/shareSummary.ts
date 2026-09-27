/**
 * Safe client-side sharing utility for Family Circle alerts.
 * Uses navigator.share() when available; falls back to clipboard.
 * Never accesses contacts or auto-sends messages.
 */

export type ShareResult = 'shared' | 'copied' | 'failed';

export async function shareOrCopySummary(
  text: string,
  title: string = 'SentryMesh Guardian Alert'
): Promise<ShareResult> {
  // Check if Web Share API is available and can share text
  if (typeof navigator !== 'undefined' && navigator.share) {
    try {
      const shareData = {
        title,
        text
      };
      if (!navigator.canShare || navigator.canShare(shareData)) {
        await navigator.share(shareData);
        return 'shared';
      }
    } catch (err: any) {
      // User cancelled share dialog (AbortError); do not fail loudly
      if (err?.name === 'AbortError') {
        return 'failed';
      }
      // Otherwise fall through to clipboard
    }
  }

  // Fallback to clipboard
  if (typeof navigator !== 'undefined' && navigator.clipboard && navigator.clipboard.writeText) {
    try {
      await navigator.clipboard.writeText(text);
      return 'copied';
    } catch {
      // Fallback for older browsers
      return fallbackCopyTextToClipboard(text);
    }
  }

  return fallbackCopyTextToClipboard(text);
}

function fallbackCopyTextToClipboard(text: string): ShareResult {
  try {
    const textArea = document.createElement('textarea');
    textArea.value = text;
    textArea.style.top = '0';
    textArea.style.left = '0';
    textArea.style.position = 'fixed';
    textArea.style.opacity = '0';
    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();
    const successful = document.execCommand('copy');
    document.body.removeChild(textArea);
    return successful ? 'copied' : 'failed';
  } catch {
    return 'failed';
  }
}
