import logging
import os
import re
import sys
import json
import time

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

            # Group into batches of 20 lines for translation
            BATCH_SIZE = 20
            batches = [srt_infos[i:i + BATCH_SIZE] for i in range(0, len(srt_infos), BATCH_SIZE)]

            max_workers = os.cpu_count() + 2

            results = thread_map(do_translate, batches, max_workers=max_workers, desc="Translating subtitle", dynamic_ncols=True, file=sys.stdout)

            translated_contents = []
            for result in results:
                translated_contents.extend(result)

            translated_contents = sorted(translated_contents, key=lambda x: x['start_time'])

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


def do_translate(batch: list[dict]):
    """Translate a batch of subtitle entries (up to 20 lines at once)."""
    target_lang = config.get_config('target_lang')
    src_lang = config.get_config()['src_lang']

    # The same language not need to be translated. Just return the original data.
    if src_lang == target_lang:
        return batch

    # Build numbered list of source texts
    source_lines = [f"{item['index']}. {item['content']}" for item in batch]
    source_block = '\n'.join(source_lines)

    prompt = f"""
    You are a Netflix subtitle translator. Please translate the following {src_lang} sentences into {"Simplified Chinese" if target_lang == "Chinese" else target_lang}.
    Do not provide any additional explanations, improvements, comments, notes or suggestions. Only provide the final translations.
    Translate each numbered sentence and return them in the same order as the following json structure:
    "translations": [
        {{"translation_text": ""}},
        {{"translation_text": ""}},
        ...
    ]
    The 'translation_text' field stores the final translation text for each corresponding sentence.
    The translations need to be more personality and modernity.
    """
    platform = config.get_config('gpt')['platform']
    api_key = config.get_config('gpt')['apiKey']
    model = config.get_config('gpt')['model']
    api = GptFactory(platform).generate_api(model, api_key)

    downgrade_result = [{'translation_text': "翻译失败"} for _ in batch]

    MAX_RETRIES = 3
    translation_list = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            translated_content: str = api.completions(prompt, source_block)
            if not translated_content:
                raise VideoEkkoError("Open api return None")

            json_pattern = re.compile(r'"translations":\s*(\[.*?\])', re.S)
            json_result = re.search(json_pattern, translated_content)

            if not json_result:
                raise VideoEkkoError("Failed to parse translation JSON from response")

            translation_list = json.loads(json_result.group(1))
            break  # success
        except Exception:
            logger.warning(f"Translation attempt {attempt}/{MAX_RETRIES} failed.")
            if attempt < MAX_RETRIES:
                time.sleep(2 ** attempt)  # exponential backoff: 2s, 4s
            else:
                logger.exception("All translation attempts failed.")

    if translation_list is None:
        translation_list = downgrade_result

    # Build result list, matching translations to original items by position
    result = []
    for i, item in enumerate(batch):
        trans_text = translation_list[i]['translation_text'] if i < len(translation_list) else "翻译失败"
        result.append({
            'index': item['index'],
            'start_time': item['start_time'],
            'end_time': item['end_time'],
            'content': f"{trans_text}\n{item['content']}"
        })
    return result


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
