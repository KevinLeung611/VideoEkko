import os
import subprocess
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ve.common import config

_WHISPER_CONFIG = config.get_config('whisper')

def transform_to_text(audio_file: str, output_dir: str):
    lang = _WHISPER_CONFIG.get('language')
    model = _WHISPER_CONFIG.get('model')

    if not lang:
        raise SystemExit("Language not specified in config.yaml")

    if not model:
        raise SystemExit("Model not specified in config.yaml")

    print(f"Executing whisper command: whisper {audio_file} --language {lang} --model {model} -o {output_dir}")

    try:
        subprocess.run(["whisper", audio_file, "--language", lang, "--model", model, "-o", output_dir],
                                    text=True)

        audio_file_name = os.path.basename(audio_file).split(".")[0]
        return {
            "srt": os.path.join(output_dir, audio_file_name + ".srt"),
            "txt": os.path.join(output_dir, audio_file_name + ".txt"),
            "vtt": os.path.join(output_dir, audio_file_name + ".vtt"),
            "tsv": os.path.join(output_dir, audio_file_name + ".tsv"),
            "json": os.path.join(output_dir, audio_file_name + ".json")
        }
    except subprocess.CalledProcessError as e:
        print(f"Transforming audio to text failed: {e}")

if __name__ == '__main__':
    from ve.common import constants
    transform_to_text(os.path.join(constants.ROOT_PATH, 'temp/breakBadHabit.wav'), os.path.join(constants.ROOT_PATH, 'temp'))