import os
import sys
import json
import asyncio
import logging
import queue
import threading

# ── Logging must be configured BEFORE importing engine (which also calls basicConfig) ──
logging.basicConfig(
    level=logging.INFO,
    handlers=[
        logging.FileHandler("logs/videoekko.log", mode="a", encoding="utf-8"),
        logging.StreamHandler(),
    ],
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    force=True,
)
logger = logging.getLogger(__name__)

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel
import engine as ve_engine
from ve.common import config as ve_config

# Ensure backend directory is on path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

app = FastAPI(title="VideoEkko API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Constants ──────────────────────────────────────────────────────────────────
_DEFAULT_PLATFORM = "deepseek"

_PLATFORMS = ["deepseek", "silicon", "openai"]

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
        platforms=_PLATFORMS,
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

    logger.info(f"Generate video request: platform={gptPlatform}, model={gptModel}, file={video.filename}")

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

    progress_queue: queue.Queue = queue.Queue()

    async def event_stream():
        try:
            # Run the engine in a thread, reporting real progress via queue
            result = {}
            error = None

            def progress_callback(step: int, message: str):
                progress_queue.put(("progress", step, message))

            def run_engine():
                nonlocal result, error
                try:
                    paths = ve_engine.generate_videos(video_path, progress_callback=progress_callback)
                    result["paths"] = paths
                except Exception as e:
                    logger.exception("Engine generate_videos failed")
                    error = str(e)
                finally:
                    progress_queue.put(("done",))

            thread = threading.Thread(target=run_engine)
            thread.start()

            while True:
                try:
                    item = await asyncio.to_thread(progress_queue.get, timeout=1)
                except queue.Empty:
                    if not thread.is_alive():
                        break
                    continue

                kind = item[0]
                if kind == "progress":
                    _, step, message = item
                    yield f"data: {json.dumps({'type': 'progress', 'step': step, 'message': message})}\n\n"
                elif kind == "done":
                    break

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
