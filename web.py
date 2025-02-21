import gradio as gr

import engine as ve_engine
from ve.common import config

_PLATFOM_MODEL_MAP = {
    "silicon": ["Qwen/Qwen2.5-72B-Instruct", "Pro/deepseek-ai/DeepSeek-R1"],
    "DeepSeek": ["R1", "V3"]
}

_WHISPER_MODEL = ["tiny", "base", "small", "medium", "large", "turbo"]

_LANG_MAP = {
    "中文": "Chinese",
    "英文": "English"
}


def gpt_platform_change(value):
    config.get_config('gpt')['platform'] = value
    return gr.Dropdown(choices=_PLATFOM_MODEL_MAP[value], value=_PLATFOM_MODEL_MAP[value][0])

def gpt_model_change(value):
    config.get_config('gpt')['model'] = value

def api_key_change(value):
    config.get_config('gpt')['api_key'] = value

def whisper_model_change(value):
    config.get_config('whisper')['model'] = value

def video_lang_change(value):
    config.get_config('whisper')['language'] = _LANG_MAP[value]

def translate_lang_change(value):
    pass

def generate_video(video_path):
    try:
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
            platform_default = 'silicon'
            gpt_platform = gr.Dropdown(_PLATFOM_MODEL_MAP.keys(), label="GPT平台", value=platform_default)
            gpt_model = gr.Dropdown(_PLATFOM_MODEL_MAP[platform_default], label="GPT模型", value=_PLATFOM_MODEL_MAP[platform_default][0])
            api_key = gr.Textbox(label="API_KEY", placeholder="请输入对应的API_KEY")
            whisper_model = gr.Dropdown(_WHISPER_MODEL, label="翻译模型", value="turbo")
            video_lang = gr.Dropdown(list(_LANG_MAP.keys()), label="原视频语言", value="英文")
            translate_lang = gr.Dropdown(list(_LANG_MAP.keys()), label="生成视频语言", value="中文")

            gpt_platform.change(gpt_platform_change, inputs=gpt_platform, outputs=gpt_model)
            gpt_model.change(gpt_model_change, inputs=gpt_model)
            api_key.blur(api_key_change, inputs=api_key)
            whisper_model.change(whisper_model_change, inputs=whisper_model)
            video_lang.change(video_lang_change, inputs=video_lang)
            translate_lang.change(translate_lang_change, inputs=translate_lang)

    with gr.Row():
        with gr.Column(scale=1):
            pass
        with gr.Column(scale=2):
            input_video = gr.PlayableVideo(sources="upload", label="上传视频")
            trans_btn = gr.Button("翻译", variant="primary")
            output_video = gr.PlayableVideo(label="生成视频")

            trans_btn.click(generate_video, inputs=input_video, outputs=output_video)
        with gr.Column(scale=1):
            pass


with gr.Blocks(theme=gr.themes.Soft()) as demo:
    show_interface(demo)
demo.launch()
