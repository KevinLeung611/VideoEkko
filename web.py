import gradio as gr

import engine as ve_engine
from ve.common import config
from ve.error import VideoEkkoError
import logging

logger = logging.getLogger(__name__)

_DEFAULT_PLATFORM = 'silicon'

_PLATFOM_MODEL_MAP = {
    "silicon": [
        "Pro/deepseek-ai/DeepSeek-V3",
        "Pro/deepseek-ai/DeepSeek-R1",
        "Qwen/Qwen2.5-72B-Instruct-128K",
        "meta-llama/Llama-3.3-70B-Instruct",
    ],
    "deepseek": [
        "deepseek-chat",
        "deepseek-reasoner"
    ],
    "openai": [
        "gpt-4o"
    ]
}

_LANG_MAP = {
    "中文": "Chinese",
    "英文": "English",
    "日语": "Japanese"
}


def page_load():
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

    return [platform, gpt_model, api_key, reverse_lang_map[video_lang],
            reverse_lang_map[translated_lang]]


def gpt_platform_change(value):
    return gr.Dropdown(choices=_PLATFOM_MODEL_MAP[value], value=_PLATFOM_MODEL_MAP[value][0])


def generate_video(gpt_platform, gpt_model, api_key, video_lang, translate_lang, video_path):
    try:
        logger.info(f"Invoking generate video api. params: {[gpt_platform, gpt_model, api_key, video_lang, translate_lang, video_path]}")

        if not api_key:
            raise gr.Error("It's require an api key. please check.")

        config.get_config('gpt')['platform'] = gpt_platform
        config.get_config('gpt')['model'] = gpt_model
        config.get_config('gpt')['apiKey'] = api_key
        config.get_config()['src_lang'] = _LANG_MAP[video_lang]
        config.get_config()['target_lang'] = _LANG_MAP[translate_lang]

        video_paths = ve_engine.generate_videos(video_path)
        if len(video_paths) == 0:
            raise VideoEkkoError("No video generated")

        return video_paths[0]
    except Exception:
        logger.exception("Invoke generate video api failed.")
        raise gr.Error("Invoke generate video api failed.")


def show_interface(demo: gr.Blocks):
    with gr.Sidebar(width=380):
        gr.Markdown(
            """
            # VideoEkko
            ### 简单易用的视频翻译工具
            **配置**
            """
        )
        with gr.Row():
            gpt_platform = gr.Dropdown(_PLATFOM_MODEL_MAP.keys(), label="GPT平台", allow_custom_value=False)

        with gr.Row():
            gpt_model = gr.Dropdown(_PLATFOM_MODEL_MAP[_DEFAULT_PLATFORM], label="GPT模型", allow_custom_value=False)

        with gr.Row():
            api_key = gr.Text(label="API_KEY", placeholder="请输入对应的API_KEY", lines=1)

        with gr.Row():
            video_lang = gr.Dropdown(list(_LANG_MAP.keys()), label="原视频语言", allow_custom_value=False)

        with gr.Row():
            translate_lang = gr.Dropdown(list(_LANG_MAP.keys()), label="生成视频语言", allow_custom_value=False)

        gpt_platform.change(gpt_platform_change, inputs=gpt_platform, outputs=gpt_model)

    with gr.Row():
        with gr.Column():
            gr.Markdown(
                """
                ### 配置说明
                - GPT平台：目前支持[silicon](https://siliconflow.cn/zh-cn/), [deepseek](https://www.deepseek.com), [openai](https://openai.com)
                - GPT模型：选择对应平台支持的大模型
                - API_KEY: 在对应的GPT平台创建好之后，配置到这里
                - 原视频语言：目前支持中文,英文,日语
                - 生成视频语言：目前支持中文,英文,日语
                    - 如果是生成中文的视频，尽量使用国内的大模型
                """
            )
        with gr.Column():
            gr.Markdown(
                """
                ### 操作步骤
                1. 在侧边栏配置相关参数，参考配置说明
                2. 上传需要翻译的视频
                3. 点击翻译按钮
                4. 等待翻译视频生成，可以在控制台查看生成进度
                """
            )
    with gr.Row():
        gr.Markdown(
            """
            ---
            **友情提示:**
            1. deepseek服务器不稳定，如果使用deepseek平台，生成时间会比较长且容易出错，建议使用 silicon
            """
        )
    with gr.Row():
        with gr.Column():
            input_video = gr.PlayableVideo(sources="upload", label="上传视频")
            trans_btn = gr.Button("翻译", variant="primary")
            output_video = gr.PlayableVideo(label="生成视频")

            trans_btn.click(generate_video,
                            inputs=[gpt_platform, gpt_model, api_key, video_lang, translate_lang,
                                    input_video],
                            outputs=output_video)

    # Page loaded config
    demo.load(fn=page_load, outputs=[gpt_platform, gpt_model, api_key, video_lang, translate_lang])


with gr.Blocks(theme=gr.themes.Soft(), title="VideoEkko", css="footer {visibility: hidden}") as demo:
    show_interface(demo)
demo.launch(server_name="0.0.0.0", server_port=7860, share=False)