# Video2Doc

将操作演示视频自动转换为步骤清晰的图文教程（Markdown 格式）。

## 功能概述

1. **音频提取** — 从视频中分离音轨
2. **语音转文字** — 调用 Whisper 模型获取带时间戳的逐句转录
3. **关键帧抽取** — 根据每句解说词的时间点自动截取对应画面
4. **图文编排** — 将转录文本 + 截图一次性交给视觉大模型，生成结构化的 Markdown 操作指南

## 环境要求

- Python 3.9+
- FFmpeg（moviepy 依赖，需提前安装）

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置密钥

将配置模板复制为 `config.py`，填入你自己的 API Key：

```bash
cp config_example.py config.py
```

然后编辑 `config.py`：

```python
API_KEY = "your-api-key-here"       # 替换为你的 API Key
API_BASE_URL = "https://api.openai.com/v1"  # 替换为你的 API 地址
VISION_MODEL = "gpt-4o"             # 替换为你使用的视觉模型
```

### 3. 放入视频

将待处理的视频文件放到项目根目录，并确保 `config.py` 中的 `VIDEO_PATH` 指向该文件：

```python
VIDEO_PATH = "demo.mp4"
```

### 4. 运行

```bash
python video2doc.py
```

运行完成后，在 `output_tutorial_pro/` 目录下可找到：

- `Ultimate_Tutorial.md` — 生成的图文教程
- `frame_0.jpg`, `frame_1.jpg`, ... — 自动截取的关键帧图片

## 项目结构

```
video2doc/
├── video2doc.py          # 主程序
├── config_example.py     # 配置模板（不含密钥）
├── config.py             # 你的实际配置（已被 .gitignore 排除）
├── requirements.txt      # Python 依赖
└── .gitignore
```

## 技术栈

| 组件 | 用途 |
|------|------|
| [moviepy](https://github.com/Zulko/moviepy) | 视频音频提取 |
| [OpenCV](https://opencv.org/) | 视频帧截取 |
| [OpenAI Whisper](https://platform.openai.com/docs/guides/speech-to-text) | 语音转文字 |
| OpenAI Vision API | 图文理解与教程生成 |

## 注意事项

- `config.py` 包含你的 API 密钥，**请勿提交到版本控制**（已在 `.gitignore` 中排除）
- 视频文件通常较大，建议也不要提交到 Git 仓库
- 生成质量取决于视频清晰度和模型能力，建议使用支持视觉理解的模型（如 GPT-4o）
