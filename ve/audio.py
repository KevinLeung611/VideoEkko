import logging
import os
import subprocess
import sys
import torch
from datetime import datetime

from pydub import AudioSegment as au
from rich.console import Console
from tqdm import tqdm

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ve.common import config
from ve.error import VideoEkkoError

logger = logging.getLogger(__name__)
console = Console()

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
        with tqdm(desc="Audio Transforming", total=len(au.from_wav(audio_file)) // 1000, dynamic_ncols=True,
                  file=sys.stdout) as tbar:

            device = 'cuda' if torch.cuda.is_available() else 'cpu'

            cmd = ["whisper", audio_file,
                   "--language", lang,
                   "--model", model,
                   "--device", device,
                   "-f", "srt",
                   "-o", output_dir]

            logger.info('Execute whisper command: %s', ' '.join(cmd))

            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

            pre_second = 0
            for line in process.stdout:
                current_end_time = line.split(']')[0].split('-->')[1].strip()
                current = datetime.strptime(current_end_time, '%M:%S.%f')
                tbar.update(current.minute * 60 + current.second - pre_second)
                pre_second = current.minute * 60 + current.second

            process.wait()
            if process.returncode != 0:
                raise subprocess.CalledProcessError(process.returncode, cmd)

            tbar.total = pre_second
            tbar.refresh()

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
