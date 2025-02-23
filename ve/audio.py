import os
import subprocess
import sys
from datetime import datetime

from pydub import AudioSegment as au
from tqdm import tqdm

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ve.common import config


def transform_to_text(audio_file: str, output_dir: str):
    lang = config.get_config()['src_lang']
    model = config.get_config('whisper')['model']

    if not lang:
        raise SystemExit("Language not specified in config.yaml")

    if not model:
        raise SystemExit("Model not specified in config.yaml")

    print(f"Executing whisper command: whisper {audio_file} --language {lang} --model {model} -f srt -o {output_dir}")

    try:
        with tqdm(desc="Audio Transforming", total=len(au.from_wav(audio_file)) // 1000, dynamic_ncols=True,
                  file=sys.stdout) as tbar:
            process = subprocess.Popen(
                ["whisper", audio_file, "--language", lang, "--model", model, "-f", "srt", "-o", output_dir],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

            pre_second = 0
            for line in process.stdout:
                current_end_time = line.split(']')[0].split('-->')[1].strip()

                current = datetime.strptime(current_end_time, '%M:%S.%f')

                tbar.update(current.minute * 60 + current.second - pre_second)

                pre_second = current.minute * 60 + current.second

            process.wait()
            tbar.total = pre_second
            tbar.refresh()

        audio_file_name = os.path.basename(audio_file).split(".")[0]
        return {
            "srt": os.path.join(output_dir, audio_file_name + ".srt")
        }
    except subprocess.CalledProcessError as e:
        print(f"Transforming audio to text failed: {e}")


if __name__ == '__main__':
    from ve.common import constants

    transform_to_text(os.path.join(constants.ROOT_PATH, 'temp/breakBadHabit.wav'),
                      os.path.join(constants.ROOT_PATH, 'temp'))
