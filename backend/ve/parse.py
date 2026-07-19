import os
import sys
from pathlib import Path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ve.common import constants

_VIDEO_SUFFIX = constants.VIDEO_SUFFIX

def retrieve_videos(video_path: str = None):
    files = [file.name for file in Path(video_path).iterdir() if file.is_file()]

    video_files = [file for file in files if file.split('.')[1] in _VIDEO_SUFFIX]

    result = []
    for video_file in video_files:
        suffix = video_file.split('.')[1]
        video_name = video_file.split('.')[0]
        result.append({
            'fullname': f"{video_name}.{suffix}",
            'name': video_name,
            'type': suffix,
            'path': os.path.join(video_path, video_file)
        })

    return result

def parse_srt_file(srt_file: str) -> list[dict]:
    result = []
    with open(srt_file, 'r', encoding='utf-8') as f:
        srt_lines = [line for line in f.readlines()]

    for i in range(0, len(srt_lines), 4):
        index = int(srt_lines[i].strip())
        time_range = srt_lines[i+1].strip()
        start_time = time_range.split(' --> ')[0]
        end_time = time_range.split(' --> ')[1]
        content = srt_lines[i+2].strip()

        result.append({
            'index': index,
            'start_time': start_time,
            'end_time': end_time,
            'content': content
        })

    return result

if __name__ == '__main__':
    print(parse_srt_file(os.path.join(constants.ROOT_PATH, 'temp/breakBadHabit.srt')))