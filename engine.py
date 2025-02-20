import os.path

from ve import audio
from ve import parse
from ve import subtitle
from ve import video
from ve.common import constants

_OUTPUT_PATH = os.path.join(constants.ROOT_PATH, 'output')
_TEMP_PATH = os.path.join(constants.ROOT_PATH, 'temp')

def main():
    video_files = parse.retrieve_videos()

    for video_file in video_files:
        print(f"Processing video: {video_file}")

        # 从视频中获取音频
        print("1️⃣Start to extract audio from video...")
        audio_path = video.extract_audio(video_file['path'], os.path.join(_TEMP_PATH, video_file['name']))

        # 将音频转成文本
        print("2️⃣Start to transform audio to text...")
        text_file_map = audio.transform_to_text(audio_path, _TEMP_PATH)

        # 将文本翻译成对应的语言
        print("3️⃣Start to translate the subtitle file...")
        translated_result = subtitle.translate(text_file_map['srt'])
        translated_file = subtitle.save(translated_result, _TEMP_PATH)

        # 将翻译后的文本写入到视频
        print("4️⃣Start to merge subtitle into video...")
        video.merge_subtitle(video_file['path'], translated_file, os.path.join(_OUTPUT_PATH, video_file['fullname']))

if __name__ == '__main__':
    main()