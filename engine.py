import os.path

from ve import audio
from ve import parse
from ve import subtitle
from ve import video
from ve.common import constants

_SOURCE_PATH = os.path.join(constants.ROOT_PATH, 'source')
_OUTPUT_PATH = os.path.join(constants.ROOT_PATH, 'output')
_TEMP_PATH = os.path.join(constants.ROOT_PATH, 'temp')

def generate_videos(video_path: str = None):
    video_files = parse.retrieve_videos(os.path.dirname(video_path)) if video_path else parse.retrieve_videos(_SOURCE_PATH)

    output_videos = []
    for video_file in video_files:
        print(f"Processing video: {video_file}")

        # Get audio from video
        print("1️⃣Start to extract audio from video...")
        audio_path = video.extract_audio(video_file['path'], os.path.join(_TEMP_PATH, video_file['name']))

        # Convert audio to text
        print("2️⃣Start to transform audio to text...")
        text_file_map = audio.transform_to_text(audio_path, _TEMP_PATH)

        # Translate text into the corresponding language
        print("3️⃣Start to translate the subtitle file...")
        translated_result = subtitle.translate(text_file_map['srt'])
        translated_file = subtitle.save(translated_result, _TEMP_PATH)

        # Write translated text to video
        print("4️⃣Start to merge subtitle into video...")
        video.merge_subtitle(video_file['path'], translated_file, os.path.join(_OUTPUT_PATH, video_file['fullname']))

        output_videos.append(os.path.join(_OUTPUT_PATH, video_file['fullname']))

    print("✅Mission Complete! Check the output result: ")
    for output in output_videos:
        print(output)

    return output_videos

if __name__ == '__main__':
    generate_videos("source")