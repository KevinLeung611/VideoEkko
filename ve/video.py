import logging
import os
import subprocess
import sys
from rich.console import Console

from tqdm import tqdm

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
logger = logging.getLogger(__name__)

console = Console()

def extract_audio(video_file: str, output_file: str):
    try:
        logger.info(f"Start to extract audio from video, params: {[video_file, output_file]}")
        logger.info(f"Executing command: ffmpeg -i {video_file} -vn -acodec pcm_s16le -ar 44100 -ac 2 {output_file + ".wav"}")

        with tqdm(desc="Extracting audio", total=1, dynamic_ncols=True, file=sys.stdout) as pbar:
            cmd = ["ffmpeg", "-i", video_file, "-vn", "-acodec", "pcm_s16le", "-ar", "44100", "-ac", "1",
                   output_file + ".wav", "-y"]

            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            process.wait()
            if process.returncode != 0:
                raise subprocess.CalledProcessError(process.returncode, cmd)
            pbar.update(1)

        return output_file + ".wav"
    except subprocess.CalledProcessError as e:
        logger.exception(f"Extracting audio failed. video file: {video_file}")
        console.print(f"Extracting audio failed: Please check logs.")
        raise e


def merge_subtitle(video_file: str, subtitle_file: str, output_file: str):
    try:
        logger.info(f"Start to merge subtitle into video, params: {[video_file, subtitle_file, output_file]}")

        with tqdm(desc="Merging subtitle", total=1, dynamic_ncols=True, file=sys.stdout) as pbar:
            cmd = ["ffmpeg",
                   "-i", video_file,
                   "-vf",
                   f"subtitles={subtitle_file}:force_style='FontName=Noto Sans CJK,FontSize=16,PrimaryColour=&HFFFFFF,Outline=1,OutlineColour=&H000000'",
                   "-c:a",
                   "copy",
                   output_file,
                   "-y"]
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            process.wait()
            if process.returncode != 0:
                raise subprocess.CalledProcessError(process.returncode, cmd)

            pbar.update(1)
    except subprocess.CalledProcessError as e:
        logger.exception("Merging subttile failed.")
        console.print(f"Merging subtitle failed: Please check logs.")
        raise e


if __name__ == '__main__':
    import os
    from ve.common import constants

    merge_subtitle(os.path.join(constants.ROOT_PATH, 'source/breakBadHabit.mp4'),
                   os.path.join(constants.ROOT_PATH, 'temp/breakBadHabit-translated.srt',),
                   os.path.join(constants.ROOT_PATH, 'output/breakBadHabit.mp4'))
