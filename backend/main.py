import os
import sys
import json
import asyncio
import logging
import threading

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel
import engine as ve_engine
from ve.common import config as ve_config

# Ensure backend directory is on path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

logging.basicConfig(
    level=logging.INFO,
    filename="logs/videoekko.log",
    filemode="a",
    encoding="utf-8",
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(title="VideoEkko API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Constants ──────────────────────────────────────────────────────────────────
_DEFAULT_PLATFORM = "silicon"

_PLATFORM_MODEL_MAP = {
    "silicon": [
        "Pro/deepseek-ai/DeepSeek-V3",
        "Pro/deepseek-ai/DeepSeek-R1",
        "Qwen/Qwen2.5-72B-Instruct-128K",
        "meta-llama/Llama-3.3-70B-Instruct",
    ],
    "deepseek": ["deepseek-chat", "deepseek-reasoner"],
    "openai": ["gpt-4o"],
}

_LANG_MAP = {
    "中文": "Chinese",
    "英文": "English",
    "日语": "Japanese",
}

_OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")

# ── Pydantic models ────────────────────────────────────────────────────────────
class GPTConfig(BaseModel):
    platform: str
    model: str
    apiKey: str

class ConfigUpdate(BaseModel):
    platform: str
    model: str
    apiKey: str
    srcLang: str  # Chinese / English / Japanese → mapped to lang code
    targetLang: str

class ConfigResponse(BaseModel):
    platform: str
    model: str
    apiKey: str
    srcLang: str
    targetLang: str
    platforms: list[str]
    models: dict


# ── API Endpoints ──────────────────────────────────────────────────────────────

@app.get("/api/config", response_model=ConfigResponse)
def get_config():
    """Get current configuration."""
    gpt_cfg = ve_config.get_config("gpt") or {}
    global_cfg = ve_config.get_config() or {}

    reverse_lang = {v: k for k, v in _LANG_MAP.items()}

    return ConfigResponse(
        platform=gpt_cfg.get("platform") or _DEFAULT_PLATFORM,
        model=gpt_cfg.get("model") or "",
        apiKey=gpt_cfg.get("apiKey") or "",
        srcLang=reverse_lang.get(global_cfg.get("src_lang", "English"), "英文"),
        targetLang=reverse_lang.get(global_cfg.get("target_lang", "Chinese"), "中文"),
        platforms=list(_PLATFORM_MODEL_MAP.keys()),
        models=_PLATFORM_MODEL_MAP,
    )


@app.put("/api/config")
def update_config(cfg: ConfigUpdate):
    """Update configuration in memory and conf.yaml."""
    gpt_section = ve_config.get_config("gpt")
    gpt_section["platform"] = cfg.platform
    gpt_section["model"] = cfg.model
    gpt_section["apiKey"] = cfg.apiKey

    root = ve_config.get_config()
    root["src_lang"] = _LANG_MAP.get(cfg.srcLang, "English")
    root["target_lang"] = _LANG_MAP.get(cfg.targetLang, "Chinese")

    return {"message": "ok"}


@app.get("/api/download/{filename}")
def download_video(filename: str):
    """Download a generated video file."""
    filepath = os.path.join(_OUTPUT_DIR, filename)
    if not os.path.isfile(filepath):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(filepath, media_type="video/mp4", filename=filename)


@app.post("/api/generate")
async def generate_video(
    gptPlatform: str = Form(...),
    gptModel: str = Form(...),
    apiKey: str = Form(...),
    srcLang: str = Form(...),
    targetLang: str = Form(...),
    video: UploadFile = File(...),
):
    """Generate a translated video. Returns SSE stream with progress and final result."""
    if not apiKey:
        raise HTTPException(status_code=400, detail="API Key is required")

    # Save uploaded video
    upload_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "source")
    os.makedirs(upload_dir, exist_ok=True)
    video_path = os.path.join(upload_dir, video.filename)
    with open(video_path, "wb") as f:
        content = await video.read()
        f.write(content)

    # Update config in memory
    ve_config.get_config("gpt")["platform"] = gptPlatform
    ve_config.get_config("gpt")["model"] = gptModel
    ve_config.get_config("gpt")["apiKey"] = apiKey
    ve_config.get_config()["src_lang"] = _LANG_MAP.get(srcLang, "English")
    ve_config.get_config()["target_lang"] = _LANG_MAP.get(targetLang, "Chinese")

    async def event_stream():
        try:
            yield f"data: {json.dumps({'type': 'progress', 'step': 1, 'message': '开始提取音频...'})}\n\n"

            # Run the engine in a thread to avoid blocking
            result = {}
            error = None

            def run_engine():
                nonlocal result, error
                try:
                    paths = ve_engine.generate_videos(video_path)
                    result["paths"] = paths
                except Exception as e:
                    error = str(e)

            thread = threading.Thread(target=run_engine)
            thread.start()

            # Poll for completion with progress updates
            step = 2
            messages = [
                "正在转换音频为文字...",
                "正在翻译字幕...",
                "正在将字幕合成到视频...",
                "正在完成...",
            ]
            msg_idx = 0
            while thread.is_alive():
                await asyncio.sleep(2)
                if msg_idx < len(messages):
                    yield f"data: {json.dumps({'type': 'progress', 'step': step, 'message': messages[msg_idx]})}\n\n"
                    step += 1
                    msg_idx += 1

            thread.join()

            if error:
                yield f"data: {json.dumps({'type': 'error', 'message': error})}\n\n"
                return

            if result.get("paths") and len(result["paths"]) > 0:
                output_path = result["paths"][0]
                filename = os.path.basename(output_path)
                yield f"data: {json.dumps({'type': 'complete', 'filename': filename})}\n\n"
            else:
                yield f"data: {json.dumps({'type': 'error', 'message': 'No video generated'})}\n\n"

        except Exception as e:
            logger.exception("Generate video failed")
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


# ── Main ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
