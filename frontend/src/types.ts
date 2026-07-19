export interface GPTConfig {
  platform: string;
  model: string;
  apiKey: string;
  srcLang: string;
  targetLang: string;
  platforms: string[];
  models: Record<string, string[]>;
}

export interface SSEMessage {
  type: 'progress' | 'complete' | 'error';
  step?: number;
  message?: string;
  filename?: string;
}
