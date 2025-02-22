import json
import os
import sys
import tqdm

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ve.gpt import silicon_api as api
from ve import parse
from ve.common import config


def translate(subtitle_file: str):
    target_lang = config.get_config('target_lang')
    src_lang = config.get_config()['src_lang']

    # prompt = f"You are a Netflix subtitle translator. Please translate the following {src_lang} sentence into {target_lang}. Do not provide any additional explanations, improvements, comments, notes or suggestions. Only provide the final translation."
    prompt = f"""
    You are a Netflix subtitle translator. Please translate the following {src_lang} sentence into {target_lang}.
    Do not provide any additional explanations, improvements, comments, notes or suggestions. Only provide the final translation.
    return the following json structure exactly:
    "translations": {{
        "origin_text": "",
        "translation_text": ""
    }}
    you can put the origin text or any additional messages to the 'origin_text' field within the translation process.
    the 'translation_text' field just stores the final translation text.
    And the translation need to be more personality and modernity.
    """

    file_name = os.path.basename(subtitle_file).split(".")[0]
    suffix_name = os.path.basename(subtitle_file).split(".")[1]

    translate_result = {}
    if suffix_name == "srt":
        srt_infos = parse.parse_srt_file(subtitle_file)
        translated_contents = []
        for srt_info in tqdm.tqdm(srt_infos, desc="Translating subtitle", ncols=100):
            response = api.completions(prompt, srt_info['content'])
            translated_content: str = response['choices'][-1]['message']['content']

            translation_info = json.loads(translated_content.split('"translations":')[1].strip())

            translated_contents.append({
                'index': srt_info['index'],
                'start_time': srt_info['start_time'],
                'end_time': srt_info['end_time'],
                'content': f"{translation_info['translation_text']}\n{srt_info['content']}"
            })

        translate_result = {
            'type': 'srt',
            'name': file_name,
            'content': translated_contents
        }

    return translate_result

def save(translate_result, output_dir: str):
    file_path = None
    if translate_result['type'] == 'srt':
        file_path = os.path.join(output_dir, translate_result['name'] + "-translated" + ".srt")
        with open(file_path, 'w') as f:
            for srt_info in translate_result['content']:
                f.write(f"{srt_info['index']}\n")
                f.write(f"{srt_info['start_time']} --> {srt_info['end_time']}\n")
                f.write(f"{srt_info['content']}\n\n")

    return file_path

if __name__ == '__main__':
    from ve.common import constants
    translate_result = translate(os.path.join(constants.ROOT_PATH, 'temp/breakBadHabit.srt'))
    save(translate_result, os.path.join(constants.ROOT_PATH, 'temp'))