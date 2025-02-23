import json
import os
import re
import sys
from concurrent.futures import ThreadPoolExecutor

from tqdm.contrib.concurrent import thread_map

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ve import parse
from ve.common import config
from ve.gpt.gpt_factory import GptFactory

thread_pool = ThreadPoolExecutor(thread_name_prefix="TranslatingPool")


def translate(subtitle_file: str):
    file_name = os.path.basename(subtitle_file).split(".")[0]
    suffix_name = os.path.basename(subtitle_file).split(".")[1]

    translate_result = {}
    if suffix_name == "srt":
        srt_infos = parse.parse_srt_file(subtitle_file)

        results = thread_map(do_translate, srt_infos, desc="Translating subtitle", dynamic_ncols=True, file=sys.stdout)

        translated_contents = []
        for result in results:
            translated_contents.append(result)

        translated_contents = sorted(translated_contents, key=lambda x:x['start_time'])

        translate_result = {
            'type': 'srt',
            'name': file_name,
            'content': translated_contents
        }

    return translate_result


def do_translate(srt_info: dict):
    target_lang = config.get_config('target_lang')
    src_lang = config.get_config()['src_lang']

    prompt = f"""
    You are a Netflix subtitle translator. Please translate the following {src_lang} sentence into {"Simplified Chinese" if target_lang == "Chinese" else target_lang}.
    Do not provide any additional explanations, improvements, comments, notes or suggestions. Only provide the final translation.
    Finally return the following json structure exactly:
    "translations": {{
        "origin_text": "",
        "translation_text": ""
    }}
    you can put the origin text or any additional messages to the 'origin_text' field within the translation process.
    The 'translation_text' field just stores the final translation text.
    And the translation need to be more personality and modernity.
    """
    platform = config.get_config('gpt')['platform']
    api_key = config.get_config('gpt')['apiKey']
    model = config.get_config('gpt')['model']
    api = GptFactory(platform).generate_api(model, api_key)

    try:
        translated_content: str = api.completions(prompt, srt_info['content'])

        json_pattern = re.compile(r'"translations":.*?({.*?})', re.S)
        json_result = re.search(json_pattern, translated_content)

        if json_result:
            translation_info = json.loads(json_result.group(1))
        else:
            raise SystemError('Json result is None')
    except (json.decoder.JSONDecodeError, SystemError) as e:
        print(f"{os.linesep}Parsing json failed. {e}")
        # 降级处理
        translation_info = {'translation_text': "翻译失败"}

    return {
        'index': srt_info['index'],
        'start_time': srt_info['start_time'],
        'end_time': srt_info['end_time'],
        'content': f"{translation_info['translation_text']}\n{srt_info['content']}"
    }


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
