import os
from dotenv import load_dotenv

# Load Environment Variables
load_dotenv()
import time
from rich.console import Console
from rich.markdown import Markdown

from ve import audio
from ve import parse
from ve import subtitle
from ve import video
from ve.common import constants

import logging

logging.basicConfig(level=logging.INFO, filename="logs/videoekko.log", filemode="a", encoding="utf-8",
                    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

logger = logging.getLogger(__name__)

_SOURCE_PATH = os.path.join(constants.ROOT_PATH, 'source')
_OUTPUT_PATH = os.path.join(constants.ROOT_PATH, 'output')
_TEMP_PATH = os.path.join(constants.ROOT_PATH, 'temp')

console = Console()

def generate_videos(input: str = None):
    logger.info(f"VideoEkko engine start. generating videos from: {input}")
    start_time = time.time()

    video_path = _SOURCE_PATH
    if input:
        if os.path.isfile(input):
            video_path = os.path.dirname(input)
        else:
            video_path = input

    video_files = parse.retrieve_videos(video_path)

    output_videos = []
    for video_file in video_files:
        try:
            # Get audio from video
            console.print(Markdown('# Step1: Extracting audio from video'))
            audio_path = video.extract_audio(video_file['path'], os.path.join(_TEMP_PATH, video_file['name']))

            # Convert audio to text
            console.print(Markdown('# Step2: Transforming audio to text'))
            text_file_map = audio.transform_to_text(audio_path, _TEMP_PATH)

            # Translate text into the corresponding language
            console.print(Markdown('# Step3: Translating subtitle file'))
            translated_result = subtitle.translate(text_file_map['srt'])
            translated_file = subtitle.save(translated_result, _TEMP_PATH)

            # Write translated text to video
            console.print(Markdown('# Step4: Merging subtitle into video'))
            video.merge_subtitle(video_file['path'], translated_file, os.path.join(_OUTPUT_PATH, video_file['fullname']))

            output_videos.append(os.path.join(_OUTPUT_PATH, video_file['fullname']))
        except Exception as e:
            logger.exception(f"Generating video failed. the video file is: {video_file}")
            raise e

    end_time = time.time()
    console.print(Markdown('# Mission Complete! Check the output result'))
    for output in output_videos:
        console.print(output, style="bold green")
    console.print(f"[b]Cost time[/b]: {round(end_time - start_time)}s")

    return output_videos

if __name__ == '__main__':
    generate_videos()