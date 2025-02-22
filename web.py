import gradio as gr

import engine as ve_engine
from ve.common import config

_DEFAULT_PLATFORM = 'silicon'

_PLATFOM_MODEL_MAP = {
    "silicon": ["Qwen/Qwen2.5-72B-Instruct", "Pro/deepseek-ai/DeepSeek-R1"],
    "DeepSeek": ["R1", "V3"]
}

_WHISPER_MODEL = ["tiny", "base", "small", "medium", "large", "turbo"]

_LANG_MAP = {
    "中文": "Chinese",
    "英文": "English",
    "日语": "Japanese"
}


def page_load():
    whisper_config = config.get_config('whisper')
    if whisper_config:
        whisper_model = 'turbo' if not whisper_config['model'] else whisper_config['model']

    gpt_config = config.get_config('gpt')
    if gpt_config:
        platform = _DEFAULT_PLATFORM if not gpt_config['platform'] else gpt_config['platform']
        api_key = gpt_config['apiKey']
        gpt_model = _PLATFOM_MODEL_MAP.get(_DEFAULT_PLATFORM)[0] if not gpt_config['model'] else gpt_config['model']

    video_lang = 'English' if not config.get_config()['src_lang'] else config.get_config()['src_lang']
    translated_lang = 'Chinese' if not config.get_config()['target_lang'] else config.get_config()['target_lang']

    reverse_lang_map = {}
    for k, v in _LANG_MAP.items():
        reverse_lang_map[v] = k


    return [platform, gpt_model, api_key, whisper_model, reverse_lang_map[video_lang], reverse_lang_map[translated_lang]]


def gpt_platform_change(value):
    return gr.Dropdown(choices=_PLATFOM_MODEL_MAP[value], value=_PLATFOM_MODEL_MAP[value][0])

def generate_video(gpt_platform, gpt_model, api_key, whisper_model, video_lang, translate_lang, video_path):
    try:
        if not api_key:
            raise gr.Error("It's require an api key. please check.")

        config.get_config('gpt')['platform'] = gpt_platform
        config.get_config('gpt')['model'] = gpt_model
        config.get_config('gpt')['apiKey'] = api_key
        config.get_config('whisper')['model'] = whisper_model
        config.get_config()['src_lang'] = _LANG_MAP[video_lang]
        config.get_config()['target_lang'] = _LANG_MAP[translate_lang]

        video_paths = ve_engine.generate_videos(video_path)
        if len(video_paths) == 0:
            raise RuntimeError("No video generated")

        print(video_paths)

        return video_paths[0]
    except Exception as e:
        print(e)
        raise gr.Error("生成视频失败")


def show_interface(demo: gr.Blocks):
    with gr.Sidebar():
        gr.Markdown(
            """
            # VideoEkko
            ### 简单易用的视频翻译工具
            **配置**
            """
        )
        with gr.Row():
            gpt_platform = gr.Dropdown(_PLATFOM_MODEL_MAP.keys(), label="GPT平台")
            gpt_model = gr.Dropdown(_PLATFOM_MODEL_MAP[_DEFAULT_PLATFORM], label="GPT模型")
            api_key = gr.Text(label="API_KEY", placeholder="请输入对应的API_KEY", lines=2)
            whisper_model = gr.Dropdown(_WHISPER_MODEL, label="翻译模型")
            video_lang = gr.Dropdown(list(_LANG_MAP.keys()), label="原视频语言")
            translate_lang = gr.Dropdown(list(_LANG_MAP.keys()), label="生成视频语言")

            gpt_platform.change(gpt_platform_change, inputs=gpt_platform, outputs=gpt_model)
    with gr.Row():
        with gr.Column(scale=1):
            pass
        with gr.Column(scale=2):
            input_video = gr.PlayableVideo(sources="upload", label="上传视频")
            trans_btn = gr.Button("翻译", variant="primary")
            output_video = gr.PlayableVideo(label="生成视频")

            trans_btn.click(generate_video,
                            inputs=[gpt_platform, gpt_model, api_key, whisper_model, video_lang, translate_lang, input_video],
                            outputs=output_video)
        with gr.Column(scale=1):
            pass

    # Page loaded config
    demo.load(fn=page_load, outputs=[gpt_platform, gpt_model, api_key, whisper_model, video_lang, translate_lang])


with gr.Blocks(theme=gr.themes.Soft()) as demo:
    show_interface(demo)
demo.launch()
