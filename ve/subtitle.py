import logging
import os
import re
import sys
import json

from rich.console import Console
from tqdm.contrib.concurrent import thread_map

from ve.error.VideoEkkoError import VideoEkkoError

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ve import parse
from ve.common import config
from ve.gpt.gpt_factory import GptFactory

logger = logging.getLogger(__name__)
console = Console()

def translate(subtitle_file: str):
    logger.info(f"Start to translate the subtitle file, params: {[subtitle_file]}")

    file_name = os.path.basename(subtitle_file).split(".")[0]
    suffix_name = os.path.basename(subtitle_file).split(".")[1]
    platform = config.get_config('gpt')['platform']

    translate_result = {}
    try:
        if suffix_name == "srt":
            srt_infos = parse.parse_srt_file(subtitle_file)

            max_workers = os.cpu_count() + 2
            # 如果是deepseek降低为1条线程，因为deepseek服务器容易超负载，返回错误数据
            if platform == 'deepseek':
                max_workers = 1

            results = thread_map(do_translate, srt_infos, max_workers=max_workers, desc="Translating subtitle", dynamic_ncols=True, file=sys.stdout)

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
    except Exception as e:
        logger.exception("Translation failed.")
        console.print("Translation failed. Please check logs.")
        raise e


def do_translate(srt_info: dict):
    target_lang = config.get_config('target_lang')
    src_lang = config.get_config()['src_lang']

    # The same language not need to be translated. Just return the original data.
    if src_lang == target_lang:
        return srt_info

    prompt = f"""
    You are a Netflix subtitle translator. Please translate the following {src_lang} sentence into {"Simplified Chinese" if target_lang == "Chinese" else target_lang}.
    Do not provide any additional explanations, improvements, comments, notes or suggestions. Only provide the final translation.
    Finally return the following json structure exactly:
    "translations": {{
        "translation_text": ""
    }}
    The 'translation_text' field just stores the final translation text.
    And the translation need to be more personality and modernity.
    """
    platform = config.get_config('gpt')['platform']
    api_key = config.get_config('gpt')['apiKey']
    model = config.get_config('gpt')['model']
    api = GptFactory(platform).generate_api(model, api_key)

    downgrade_result = {'translation_text': "翻译失败"}  # 降级结果
    try:
        translated_content: str = api.completions(prompt, srt_info['content'])
        if not translated_content:
            raise VideoEkkoError("Open api return None")

        json_pattern = re.compile(r'"translations":.*?({.*?})', re.S)
        json_result = re.search(json_pattern, translated_content)

        translation_info = json.loads(json_result.group(1)) if json_result else downgrade_result
    except Exception:
        logger.exception("Invoke open api failed.")
        translation_info = downgrade_result

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
