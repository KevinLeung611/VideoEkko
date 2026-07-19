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
├── install.py              # 一键安装脚本
├── backend/                # Python FastAPI 后端
│   ├── main.py             # API 入口
│   ├── engine.py           # 核心引擎
│   ├── ve/                 # 引擎模块 (audio, video, subtitle, gpt)
│   ├── conf.yaml           # 配置文件
│   └── pyproject.toml      # Python 依赖 (uv)
├── frontend/               # React + Tailwind + TypeScript 前端
│   ├── src/
│   │   ├── components/     # React 组件
│   │   ├── api/            # API 客户端
│   │   └── App.tsx         # 主应用
│   └── package.json        # Node 依赖
└── package.json            # Monorepo 根配置
```

## 🥳 安装方法

### 前置要求
- [Python 3.12+](https://www.python.org/downloads/)
- [uv](https://docs.astral.sh/uv/) — Python 包管理器
- [Node.js](https://nodejs.org/) — 前端运行时
- [Homebrew](https://brew.sh) (macOS) — 用于安装 ffmpeg

### 一键安装

```shell
npm install        # 安装前端依赖，然后自动执行 install.py 配置后端
```

`npm install` 会自动触发 `postinstall` 脚本，完成：
- 安装 ffmpeg（macOS 自动安装 ffmpeg-full，含字幕渲染支持）
- 安装 OpenAI Whisper
- 同步 Python 依赖（uv sync）

### 手动安装

如果自动安装失败，可以单独执行后端安装脚本：

```shell
./install.py       # 或者：python3 install.py
```

## 🛠️ 使用方法

### Web 页面（推荐）

```shell
npm start          # 一键启动前后端，浏览器打开 http://localhost:5173
```

或者分别启动：

```shell
# 终端 1：启动后端
npm run backend

# 终端 2：启动前端
npm run dev
```

### 命令行

```shell
# 1. 将需要操作的视频放进 backend/source 文件夹中
# 2. 配置 backend/conf.yaml
# 3. 执行处理引擎
cd backend && uv run python engine.py
```

## 🤔 技术栈

- **前端**: React 18 + TypeScript + Tailwind CSS + Vite
- **后端**: Python + FastAPI + Uvicorn
- **包管理**: uv (Python)、npm (Node)
- **语音识别**: OpenAI Whisper
- **翻译**: GPT API (SiliconFlow / DeepSeek / OpenAI)
- **视频处理**: FFmpeg (macOS 需 ffmpeg-full 以获得 libass 字幕支持)

## License
VideoEkko is released under the MIT License. See [LICENSE](./LICENSE) for further details.
