import os.path
from dotenv import load_dotenv
# Load Environment Variables
load_dotenv()
import time

from ve import audio
from ve import parse
from ve import subtitle
from ve import video
from ve.common import constants

_SOURCE_PATH = os.path.join(constants.ROOT_PATH, 'source')
_OUTPUT_PATH = os.path.join(constants.ROOT_PATH, 'output')
_TEMP_PATH = os.path.join(constants.ROOT_PATH, 'temp')

def generate_videos(video_path: str = None):
    start_time = time.time()

    video_files = parse.retrieve_videos(os.path.dirname(video_path)) if video_path else parse.retrieve_videos(_SOURCE_PATH)

    output_videos = []
    for video_file in video_files:
        # Get audio from video
        print(f"😄 Start to extract audio from video [{video_file['path']}]")
        audio_path = video.extract_audio(video_file['path'], os.path.join(_TEMP_PATH, video_file['name']))

        # Convert audio to text
        print("🙈 Start to transform audio to text...")
        text_file_map = audio.transform_to_text(audio_path, _TEMP_PATH)

        # Translate text into the corresponding language
        print("😎 Start to translate the subtitle file...")
        translated_result = subtitle.translate(text_file_map['srt'])
        translated_file = subtitle.save(translated_result, _TEMP_PATH)

        # Write translated text to video
        print("🤣 Start to merge subtitle into video...")
        video.merge_subtitle(video_file['path'], translated_file, os.path.join(_OUTPUT_PATH, video_file['fullname']))

        output_videos.append(os.path.join(_OUTPUT_PATH, video_file['fullname']))

    end_time = time.time()
    print("✅ Mission Complete! Check the output result: ")
    for output in output_videos:
        print(output)
    print(f"Cost time: {round(end_time - start_time)}s")

    return output_videos

if __name__ == '__main__':
    generate_videos()