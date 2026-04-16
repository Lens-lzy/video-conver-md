# ================= 全局配置文件 =================
# 使用前请将此文件复制为 config.py 并填入你的真实密钥：
#   cp config_example.py config.py

# ---------- OpenAI / AI 网关配置 ----------
API_KEY = "your-api-key-here"
API_BASE_URL = "https://api.openai.com/v1"

# ---------- 模型配置 ----------
AUDIO_MODEL = "whisper-1"
VISION_MODEL = "gpt-4o"
MAX_TOKENS = 4000
TEMPERATURE = 0.3

# ---------- 文件路径配置 ----------
VIDEO_PATH = "demo.mp4"
AUDIO_PATH = "temp_audio.mp3"
OUTPUT_DIR = "output_tutorial_pro"
