import { useState } from 'react';
import Sidebar from './components/Sidebar';
import VideoUploader from './components/VideoUploader';
import type { GPTConfig, SSEMessage } from './types';
import { fetchConfig } from './api/client';

export default function App() {
  const [config, setConfig] = useState<GPTConfig | null>(null);
  const [loading, setLoading] = useState(true);

  // Config handlers
  const handleConfigLoaded = (cfg: GPTConfig) => {
    setConfig(cfg);
    setLoading(false);
  };

  const handleConfigChange = (partial: Partial<GPTConfig>) => {
    setConfig((prev) => (prev ? { ...prev, ...partial } : prev));
  };

  return (
    <div className="flex h-screen overflow-hidden">
      {/* Sidebar */}
      <Sidebar
        config={config}
        loading={loading}
        onConfigLoaded={handleConfigLoaded}
        onConfigChange={handleConfigChange}
      />

      {/* Main content */}
      <main className="flex-1 overflow-y-auto">
        <div className="mx-auto max-w-4xl px-6 py-8">
          <div className="mb-8">
            <h1 className="text-3xl font-bold tracking-tight text-gray-900">
              VideoEkko
            </h1>
            <p className="mt-2 text-gray-500">简单易用的视频翻译工具</p>
          </div>

          {loading ? (
            <div className="flex items-center justify-center py-20">
              <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary-200 border-t-primary-600" />
              <span className="ml-3 text-gray-500">加载配置中...</span>
            </div>
          ) : (
            <VideoUploader config={config!} />
          )}

          {/* Instructions */}
          <div className="mt-12 grid gap-6 md:grid-cols-2">
            <div className="rounded-xl border border-gray-200 bg-white p-6">
              <h3 className="mb-3 text-lg font-semibold text-gray-800">配置说明</h3>
              <ul className="space-y-2 text-sm text-gray-600">
                <li>
                  · GPT平台：支持
                  <a href="https://siliconflow.cn" className="text-primary-600 hover:underline" target="_blank" rel="noreferrer"> SiliconFlow</a>、
                  <a href="https://www.deepseek.com" className="text-primary-600 hover:underline" target="_blank" rel="noreferrer"> DeepSeek</a>、
                  <a href="https://openai.com" className="text-primary-600 hover:underline" target="_blank" rel="noreferrer"> OpenAI</a>
                </li>
                <li>· API_KEY: 在对应平台创建后配置到侧边栏</li>
                <li>· 支持中文、英文、日语互译</li>
                <li>· 生成中文视频建议使用国内大模型</li>
              </ul>
            </div>
            <div className="rounded-xl border border-gray-200 bg-white p-6">
              <h3 className="mb-3 text-lg font-semibold text-gray-800">操作步骤</h3>
              <ol className="space-y-2 text-sm text-gray-600">
                <li>1. 在侧边栏配置 API Key 和翻译参数</li>
                <li>2. 上传需要翻译的视频</li>
                <li>3. 点击「开始翻译」按钮</li>
                <li>4. 等待视频生成完成，下载结果</li>
              </ol>
            </div>
          </div>

          {/* Tip */}
          <div className="mt-6 rounded-xl border border-amber-200 bg-amber-50 p-4">
            <p className="text-sm text-amber-700">
              ⚠️ 友情提示：DeepSeek 服务器不稳定，使用 DeepSeek 平台生成时间可能较长且容易出错，建议使用 SiliconFlow。
            </p>
          </div>
        </div>
      </main>
    </div>
  );
}
