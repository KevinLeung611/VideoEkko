import subprocess
import sys

from tqdm import tqdm


def extract_audio(video_file: str, output_file: str):
    try:
        print(f"Executing command: ffmpeg -i {video_file} -vn -acodec pcm_s16le -ar 44100 -ac 2 {output_file + ".wav"}")

        with tqdm(desc="Extracting audio", total=1, dynamic_ncols=True, file=sys.stdout) as pbar:
            cmd = ["ffmpeg", "-i", video_file, "-vn", "-acodec", "pcm_s16le", "-ar", "44100", "-ac", "1",
                   output_file + ".wav", "-y"]

            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            process.wait()
            pbar.update(1)

        return output_file + ".wav"
    except subprocess.CalledProcessError as e:
        print(f"Extracting audio failed: {e}")


def merge_subtitle(video_file: str, subtitle_file: str, output_file: str):
    with tqdm(desc="Merging subtitle", total=1, dynamic_ncols=True, file=sys.stdout) as pbar:
        cmd = ["ffmpeg", "-i", video_file, "-vf",
               f"subtitles={subtitle_file}:force_style='FontName=Yuanti SC,FontSize=12,PrimaryColour=&HFFFFFF,Outline=1,OutlineColour=&H000000'",
               "-c:a", "copy", output_file, "-y"]
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        process.wait()
        pbar.update(1)


if __name__ == '__main__':
    import os
    from ve.common import constants

    extract_audio(os.path.join(constants.ROOT_PATH, 'source/breakBadHabit.mp4'),
                  os.path.join(constants.ROOT_PATH, 'temp/breakBadHabit'))
