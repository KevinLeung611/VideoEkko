import logging
import os
import subprocess
import sys
import torch
import wave
from datetime import datetime

from rich.console import Console
from tqdm import tqdm

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ve.common import config
from ve.error import VideoEkkoError

logger = logging.getLogger(__name__)
console = Console()

def _get_wav_duration_seconds(audio_file: str) -> int:
    with wave.open(audio_file, 'rb') as wav_file:
        return int(wav_file.getnframes() / wav_file.getframerate())

def transform_to_text(audio_file: str, output_dir: str):
    logger.info(f"Start to transform audio to text, params: {[audio_file, output_dir]}")
    lang = config.get_config()['src_lang']
    model = config.get_config('whisper')['model']

    whisper_model = config.get_config('whisper')['model']
    if config.get_config()['src_lang'] != 'English':
        if whisper_model not in ['large', 'turbo']:
            model = 'turbo'

    if not lang:
        raise VideoEkkoError("Language not specified in config.yaml")

    if not model:
        raise VideoEkkoError("Model not specified in config.yaml")

    try:
        audio_duration = _get_wav_duration_seconds(audio_file)

        device = 'cuda' if torch.cuda.is_available() else 'cpu'

        cmd = ["whisper", audio_file,
               "--language", lang,
               "--model", model,
               "--device", device,
               "-f", "srt",
               "-o", output_dir]

        logger.info('Execute whisper command: %s', ' '.join(cmd))

        # Use Popen with a thread to drain stderr — avoids deadlock when whisper
        # downloads the model or emits warnings to stderr during transcription.
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        # Drain stderr in a background thread: show download progress in real-time
        # while capturing everything for error diagnosis.
        stderr_lines: list[str] = []
        import threading

        def _drain_stderr():
            """Read stderr char-by-char so we can display tqdm-style \\r progress lines."""
            buf = ""
            while True:
                ch = process.stderr.read(1)
                if not ch:
                    break
                buf += ch
                if ch == "\n":
                    line = buf.rstrip("\r\n")
                    stderr_lines.append(line)
                    # Show non-progress lines dimmed, progress lines as-is
                    if line and "%" in line and "|" in line:
                        sys.stderr.write(f"\r  {line}")
                        sys.stderr.flush()
                    elif line:
                        sys.stderr.write(f"\r  {line}\n")
                        sys.stderr.flush()
                    buf = ""
                elif ch == "\r":
                    # tqdm uses \r without \n to update in place
                    if buf.rstrip("\r") and "%" in buf and "|" in buf:
                        sys.stderr.write(f"\r  {buf.rstrip()}")
                        sys.stderr.flush()
                        stderr_lines.append(buf.rstrip("\r"))
                        buf = ""
                    else:
                        buf = ""  # discard bare \r

            # Flush remaining buffer
            if buf.strip():
                stderr_lines.append(buf.strip())

        stderr_thread = threading.Thread(target=_drain_stderr, daemon=True)
        stderr_thread.start()

        with tqdm(desc="Audio Transforming", total=audio_duration, dynamic_ncols=True,
                  file=sys.stdout) as tbar:

            pre_second = 0
            for line in process.stdout:
                # whisper outputs "[HH:MM.SS --> HH:MM.SS] text" for each segment
                if "-->" not in line or "]" not in line:
                    continue  # skip model-loading / info lines
                try:
                    current_end_time = line.split("]")[0].split("-->")[1].strip()
                    current = datetime.strptime(current_end_time, "%M:%S.%f")
                    delta = current.minute * 60 + current.second - pre_second
                    if delta > 0:
                        tbar.update(delta)
                        pre_second = current.minute * 60 + current.second
                except (ValueError, IndexError):
                    continue

            process.wait()
            stderr_thread.join(timeout=5)

            tbar.total = pre_second
            tbar.refresh()

        if process.returncode != 0:
            stderr_tail = "".join(stderr_lines[-20:]) if stderr_lines else ""
            logger.error(f"Whisper failed with code {process.returncode}:\n{stderr_tail}")
            raise subprocess.CalledProcessError(process.returncode, cmd)

        audio_file_name = os.path.basename(audio_file).split(".")[0]
        return {
            "srt": os.path.join(output_dir, audio_file_name + ".srt")
        }
    except subprocess.CalledProcessError as e:
        logger.exception(f"Transforming audio to text failed. audio file: {audio_file}")
        console.print("Transforming audio to text failed. Please check logs.")
        raise e


if __name__ == '__main__':
    from ve.common import constants

    transform_to_text(os.path.join(constants.ROOT_PATH, 'temp/breakBadHabit.wav'),
                      os.path.join(constants.ROOT_PATH, 'temp'))
