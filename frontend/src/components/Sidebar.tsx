import { useEffect } from 'react';
import type { GPTConfig } from '../types';
import { fetchConfig, updateConfig } from '../api/client';

interface Props {
  config: GPTConfig | null;
  loading: boolean;
  onConfigLoaded: (cfg: GPTConfig) => void;
  onConfigChange: (partial: Partial<GPTConfig>) => void;
}

const LANG_OPTIONS = ['中文', '英文', '日语'];

export default function Sidebar({ config, loading, onConfigLoaded, onConfigChange }: Props) {
  useEffect(() => {
    fetchConfig()
      .then(onConfigLoaded)
      .catch((err) => console.error('Failed to load config:', err));
  }, []);

  const handleSave = async () => {
    if (!config) return;
    try {
      await updateConfig({
        platform: config.platform,
        model: config.model,
        apiKey: config.apiKey,
        srcLang: config.srcLang,
        targetLang: config.targetLang,
      });
    } catch (err) {
      console.error('Failed to save config:', err);
    }
  };

  const models = config?.models[config?.platform] || [];

  return (
    <aside className="flex w-[340px] shrink-0 flex-col border-r border-gray-200 bg-white">
      <div className="border-b border-gray-100 px-5 py-4">
        <h2 className="text-lg font-bold text-gray-800">⚙️ 配置</h2>
      </div>

      <div className="flex-1 space-y-4 overflow-y-auto px-5 py-4">
        {/* Platform */}
        <div>
          <label className="mb-1 block text-sm font-medium text-gray-700">GPT平台</label>
          <select
            className="select-field"
            value={config?.platform || ''}
            onChange={(e) => onConfigChange({ platform: e.target.value, model: '' })}
            disabled={loading}
          >
            {(config?.platforms || []).map((p) => (
              <option key={p} value={p}>{p}</option>
            ))}
          </select>
        </div>

        {/* Model */}
        <div>
          <label className="mb-1 block text-sm font-medium text-gray-700">GPT模型</label>
          <select
            className="select-field"
            value={config?.model || ''}
            onChange={(e) => onConfigChange({ model: e.target.value })}
            disabled={loading}
          >
            <option value="">请选择模型</option>
            {models.map((m) => (
              <option key={m} value={m}>{m}</option>
            ))}
          </select>
        </div>

        {/* API Key */}
        <div>
          <label className="mb-1 block text-sm font-medium text-gray-700">API_KEY</label>
          <input
            type="password"
            className="input-field"
            placeholder="请输入对应的 API_KEY"
            value={config?.apiKey || ''}
            onChange={(e) => onConfigChange({ apiKey: e.target.value })}
            disabled={loading}
          />
        </div>

        {/* Source language */}
        <div>
          <label className="mb-1 block text-sm font-medium text-gray-700">原视频语言</label>
          <select
            className="select-field"
            value={config?.srcLang || '英文'}
            onChange={(e) => onConfigChange({ srcLang: e.target.value })}
            disabled={loading}
          >
            {LANG_OPTIONS.map((l) => (
              <option key={l} value={l}>{l}</option>
            ))}
          </select>
        </div>

        {/* Target language */}
        <div>
          <label className="mb-1 block text-sm font-medium text-gray-700">生成视频语言</label>
          <select
            className="select-field"
            value={config?.targetLang || '中文'}
            onChange={(e) => onConfigChange({ targetLang: e.target.value })}
            disabled={loading}
          >
            {LANG_OPTIONS.map((l) => (
              <option key={l} value={l}>{l}</option>
            ))}
          </select>
        </div>
      </div>

      <div className="border-t border-gray-100 px-5 py-4">
        <button
          className="btn-primary w-full"
          onClick={handleSave}
          disabled={loading || !config?.apiKey}
        >
          保存配置
        </button>
      </div>
    </aside>
  );
}
