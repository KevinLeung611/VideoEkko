import { useState, useRef, useCallback } from 'react';
import type { GPTConfig, SSEMessage } from '../types';
import { generateVideo, getDownloadUrl } from '../api/client';

interface Props {
  config: GPTConfig;
}

type Status = 'idle' | 'uploading' | 'generating' | 'complete' | 'error';

export default function VideoUploader({ config }: Props) {
  const [videoFile, setVideoFile] = useState<File | null>(null);
  const [videoPreviewUrl, setVideoPreviewUrl] = useState<string | null>(null);
  const [status, setStatus] = useState<Status>('idle');
  const [progressMsg, setProgressMsg] = useState('');
  const [progressStep, setProgressStep] = useState(0);
  const [outputFilename, setOutputFilename] = useState<string | null>(null);
  const [errorMsg, setErrorMsg] = useState('');
  const [isDragOver, setIsDragOver] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const abortRef = useRef<AbortController | null>(null);

  const steps = ['提取音频', '语音转文字', '翻译字幕', '合成字幕'];
  const totalSteps = steps.length;

  const handleFile = useCallback((file: File) => {
    if (!file.type.startsWith('video/')) {
      setErrorMsg('请上传视频文件');
      return;
    }
    setVideoFile(file);
    setVideoPreviewUrl(URL.createObjectURL(file));
    setStatus('idle');
    setOutputFilename(null);
    setErrorMsg('');
  }, []);

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setIsDragOver(false);
      const file = e.dataTransfer.files[0];
      if (file) handleFile(file);
    },
    [handleFile],
  );

  const handleStart = async () => {
    if (!videoFile || !config.apiKey) return;

    setStatus('generating');
    setProgressStep(0);
    setProgressMsg('正在准备...');
    setErrorMsg('');
    setOutputFilename(null);

    abortRef.current = generateVideo(
      {
        gptPlatform: config.platform,
        gptModel: config.model,
        apiKey: config.apiKey,
        srcLang: config.srcLang,
        targetLang: config.targetLang,
        video: videoFile,
      },
      (msg: SSEMessage) => {
        if (msg.type === 'progress') {
          setProgressStep((msg.step || 1) - 1);
          setProgressMsg(msg.message || '');
        }
      },
      (err: string) => {
        setStatus('error');
        setErrorMsg(err);
      },
      (filename: string) => {
        setStatus('complete');
        setOutputFilename(filename);
        setProgressStep(totalSteps);
        setProgressMsg('翻译完成！');
      },
    );
  };

  const handleCancel = () => {
    abortRef.current?.abort();
    setStatus('idle');
    setProgressMsg('');
    setProgressStep(0);
  };

  const progressPercent = Math.round((progressStep / totalSteps) * 100);

  return (
    <div className="space-y-6">
      {/* Upload area */}
      {status !== 'generating' && (
        <div
          className={`relative rounded-2xl border-2 border-dashed p-12 text-center transition-all duration-200 ${
            isDragOver
              ? 'border-primary-400 bg-primary-50'
              : videoFile
                ? 'border-green-300 bg-green-50'
                : 'border-gray-300 bg-gray-50 hover:border-gray-400'
          }`}
          onDragOver={(e) => {
            e.preventDefault();
            setIsDragOver(true);
          }}
          onDragLeave={() => setIsDragOver(false)}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
        >
          <input
            ref={fileInputRef}
            type="file"
            accept="video/*"
            className="hidden"
            onChange={(e) => {
              const file = e.target.files?.[0];
              if (file) handleFile(file);
            }}
          />

          {videoFile ? (
            <div className="space-y-3">
              <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-full bg-green-100">
                <svg className="h-7 w-7 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                </svg>
              </div>
              <p className="font-medium text-gray-700">{videoFile.name}</p>
              <p className="text-sm text-gray-400">
                {(videoFile.size / (1024 * 1024)).toFixed(1)} MB · 点击重新上传
              </p>
            </div>
          ) : (
            <div className="space-y-3">
              <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-full bg-gray-200">
                <svg className="h-7 w-7 text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5m-13.5-9L12 3m0 0l4.5 4.5M12 3v13.5" />
                </svg>
              </div>
              <p className="font-medium text-gray-600">拖拽视频到此处，或点击上传</p>
              <p className="text-sm text-gray-400">支持 MP4、MKV、AVI、MOV 等常见格式</p>
            </div>
          )}
        </div>
      )}

      {/* Video preview */}
      {videoPreviewUrl && status !== 'generating' && (
        <div className="overflow-hidden rounded-xl border border-gray-200 bg-black">
          <video src={videoPreviewUrl} controls className="max-h-[400px] w-full" />
        </div>
      )}

      {/* Progress */}
      {status === 'generating' && (
        <div className="rounded-2xl border border-gray-200 bg-white p-8">
          <div className="mb-6">
            <div className="mb-2 flex items-center justify-between text-sm">
              <span className="font-medium text-gray-700">{progressMsg}</span>
              <span className="text-gray-400">{progressPercent}%</span>
            </div>
            <div className="h-2.5 w-full overflow-hidden rounded-full bg-gray-100">
              <div
                className="h-full rounded-full bg-primary-500 transition-all duration-700 ease-out"
                style={{ width: `${progressPercent}%` }}
              />
            </div>
          </div>

          <div className="space-y-2">
            {steps.map((label, i) => (
              <div key={i} className="flex items-center gap-3 text-sm">
                {i < progressStep ? (
                  <svg className="h-5 w-5 shrink-0 text-green-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                  </svg>
                ) : i === progressStep ? (
                  <div className="h-5 w-5 shrink-0 animate-spin rounded-full border-2 border-primary-300 border-t-primary-600" />
                ) : (
                  <div className="h-5 w-5 shrink-0 rounded-full border-2 border-gray-200" />
                )}
                <span className={i < progressStep ? 'text-green-600' : i === progressStep ? 'font-medium text-primary-600' : 'text-gray-400'}>
                  {label}
                </span>
              </div>
            ))}
          </div>

          <button
            className="mt-6 text-sm text-gray-400 underline hover:text-gray-600"
            onClick={handleCancel}
          >
            取消
          </button>
        </div>
      )}

      {/* Error */}
      {status === 'error' && (
        <div className="rounded-xl border border-red-200 bg-red-50 p-4">
          <p className="text-sm font-medium text-red-700">❌ {errorMsg}</p>
          <button
            className="mt-2 text-sm text-red-500 underline hover:text-red-700"
            onClick={() => setStatus('idle')}
          >
            重试
          </button>
        </div>
      )}

      {/* Complete */}
      {status === 'complete' && outputFilename && (
        <div className="rounded-2xl border border-green-200 bg-green-50 p-8 text-center">
          <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-green-100">
            <svg className="h-8 w-8 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
            </svg>
          </div>
          <h3 className="mb-2 text-lg font-semibold text-gray-800">翻译完成！</h3>
          <p className="mb-6 text-sm text-gray-500">视频已生成，点击下方按钮下载</p>

          {/* Output video preview */}
          <div className="mb-6 overflow-hidden rounded-xl border border-gray-200 bg-black">
            <video
              src={getDownloadUrl(outputFilename)}
              controls
              className="max-h-[400px] w-full"
            />
          </div>

          <div className="flex items-center justify-center gap-3">
            <a
              href={getDownloadUrl(outputFilename)}
              download
              className="btn-primary"
            >
              下载视频
            </a>
            <button
              className="rounded-lg border border-gray-300 px-6 py-2.5 text-sm font-medium text-gray-700 transition-colors hover:bg-gray-50"
              onClick={() => {
                setStatus('idle');
                setVideoFile(null);
                setVideoPreviewUrl(null);
                setOutputFilename(null);
              }}
            >
              翻译新视频
            </button>
          </div>
        </div>
      )}

      {/* Start button */}
      {status === 'idle' && videoFile && (
        <button
          className="btn-primary w-full py-3 text-base"
          onClick={handleStart}
          disabled={!config.apiKey || !config.model}
        >
          开始翻译
        </button>
      )}
    </div>
  );
}
