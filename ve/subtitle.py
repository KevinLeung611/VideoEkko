import os
import sys

import progressbar

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ve.gpt import silicon_api as api
from ve import parse


def translate(subtitle_file: str):
    prompt = "You are a professional translator. Please translate the following text to chinese."

    file_name = os.path.basename(subtitle_file).split(".")[0]
    suffix_name = os.path.basename(subtitle_file).split(".")[1]

    translate_result = {}
    if suffix_name == "srt":
        srt_infos = parse.parse_srt_file(subtitle_file)
        translated_contents = []
        bar = progressbar.ProgressBar(max_value=len(srt_infos), widgets=['Translating...', ' [', progressbar.Percentage(), '] ', progressbar.Bar()])
        bar.start()
        for i, srt_info in enumerate(srt_infos):
            response = api.completions(prompt, srt_info['content'])
            translated_content = response['choices'][0]['message']['content']

            translated_contents.append({
                'index': srt_info['index'],
                'start_time': srt_info['start_time'],
                'end_time': srt_info['end_time'],
                'content': f"{translated_content}\n{srt_info['content']}"
            })
            bar.update(i + 1)

        bar.finish()
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
    pass