# 👉🏻 VideoEkko 👈🏻

[![SVG Banners](https://svg-banners.vercel.app/api?type=luminance&text1=VideoEkko%20📹&width=800&height=300)](https://github.com/Akshay090/svg-banners)

## 👍🏻 简介
VideoEkko — 快速为您的视频添加翻译字幕
* 简单配置，轻松上手
* 高效生成，节省时间
* 支持多语言翻译，全球通用
* 一键安装与部署，免去繁琐步骤
* 兼容多种 GPT 集成平台

## 👀 Demo

<table>
<tr>
<td>

### 原视频
---
https://github.com/user-attachments/assets/877c5575-2cc1-482f-82a5-c33f4f576ea2

</td>
<td>

### 生成视频
---
https://github.com/user-attachments/assets/d6c4e463-d719-41b1-bb61-c05e51009172

</td>
</tr>
</table>

## 🏗️ 项目结构

```
VideoEkko/
├── backend/                # Python FastAPI 后端
│   ├── main.py             # API 入口
│   ├── engine.py           # 核心引擎
│   ├── ve/                 # 引擎模块 (audio, video, subtitle, gpt)
│   ├── conf.yaml           # 配置文件
│   └── requirements.txt    # Python 依赖
├── frontend/               # React + Tailwind + TypeScript 前端
│   ├── src/
│   │   ├── components/     # React 组件
│   │   ├── api/            # API 客户端
│   │   └── App.tsx         # 主应用
│   └── package.json        # Node 依赖
└── package.json            # Monorepo 根配置
```

## 🥳 安装方法

VideoEkko 依赖 **ffmpeg** 和 **whisper**

### 一键安装
```shell
# 创建 conda 虚拟环境
conda create -n videoekko -y python=3.12
# 激活环境
conda activate videoekko
# 启动安装脚本
cd backend && python install.py
```

### 手动安装依赖

1. **安装 [ffmpeg](https://www.ffmpeg.org)**

```shell
# Ubuntu/Debian
sudo apt install -y ffmpeg

# CentOS/Fedora
sudo yum install -y ffmpeg

# MacOS
brew install ffmpeg

# Windows
choco install ffmpeg
```

2. **安装 [whisper](https://github.com/openai/whisper)**

```shell
pip install -U openai-whisper
```

3. **安装 Python 依赖**

```shell
cd backend
pip install -r requirements.txt
```

4. **安装前端依赖**

```shell
cd frontend
npm install
```

## 🛠️ 使用方法

### Web 页面（推荐）

```shell
# 1. 启动后端 API 服务
cd backend
python main.py

# 2. 启动前端开发服务器（新终端）
cd frontend
npm run dev

# 3. 浏览器打开 http://localhost:5173
```

### 命令行

```shell
# 1. 将需要操作的视频放进 backend/source 文件夹中
# 2. 配置 backend/conf.yaml
# 3. 执行处理引擎
cd backend && python engine.py
```

## 🤔 技术栈

- **前端**: React 18 + TypeScript + Tailwind CSS + Vite
- **后端**: Python + FastAPI + Uvicorn
- **语音识别**: OpenAI Whisper
- **翻译**: GPT API (SiliconFlow / DeepSeek / OpenAI)
- **视频处理**: FFmpeg

## License
VideoEkko is released under the MIT License. See [LICENSE](./LICENSE) for further details.
