import type { GPTConfig, SSEMessage } from '../types';

const BASE = 'http://localhost:8000/api';

export async function fetchConfig(): Promise<GPTConfig> {
  const res = await fetch(`${BASE}/config`);
  if (!res.ok) throw new Error('Failed to fetch config');
  return res.json();
}

export async function updateConfig(cfg: {
  platform: string;
  model: string;
  apiKey: string;
  srcLang: string;
  targetLang: string;
}): Promise<void> {
  const res = await fetch(`${BASE}/config`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(cfg),
  });
  if (!res.ok) throw new Error('Failed to update config');
}

export function generateVideo(
  params: {
    gptPlatform: string;
    gptModel: string;
    apiKey: string;
    srcLang: string;
    targetLang: string;
    video: File;
  },
  onMessage: (msg: SSEMessage) => void,
  onError: (err: string) => void,
  onComplete: (filename: string) => void,
): AbortController {
  const controller = new AbortController();
  const formData = new FormData();
  formData.append('gptPlatform', params.gptPlatform);
  formData.append('gptModel', params.gptModel);
  formData.append('apiKey', params.apiKey);
  formData.append('srcLang', params.srcLang);
  formData.append('targetLang', params.targetLang);
  formData.append('video', params.video);

  fetch(`${BASE}/generate`, {
    method: 'POST',
    body: formData,
    signal: controller.signal,
  })
    .then(async (res) => {
      if (!res.ok) throw new Error('Request failed');
      const reader = res.body?.getReader();
      if (!reader) throw new Error('No response body');

      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6));
              onMessage(data);
              if (data.type === 'error') onError(data.message || 'Unknown error');
              if (data.type === 'complete') onComplete(data.filename);
            } catch {
              // skip unparseable lines
            }
          }
        }
      }
    })
    .catch((err) => {
      if (err.name !== 'AbortError') {
        onError(err.message || 'Request failed');
      }
    });

  return controller;
}

export function getDownloadUrl(filename: string): string {
  return `${BASE}/download/${encodeURIComponent(filename)}`;
}
