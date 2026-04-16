import os
import cv2
import base64
from moviepy import VideoFileClip
from openai import OpenAI
from config import (
    API_KEY, API_BASE_URL,
    AUDIO_MODEL, VISION_MODEL, MAX_TOKENS, TEMPERATURE,
    VIDEO_PATH, AUDIO_PATH, OUTPUT_DIR,
)


def encode_image(image_path):
    """将图片编码为 base64 字符串"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def extract_audio(video_path, audio_path):
    """从视频中提取音频"""
    print("正在提取视频音频...")
    video = VideoFileClip(video_path)
    video.audio.write_audiofile(audio_path, logger=None)
    video.close()


def transcribe_audio(client, audio_path):
    """调用 Whisper 模型识别音频，返回带时间戳的片段列表"""
    print(f"正在调用 {AUDIO_MODEL} 识别音频并提取时间线...")
    with open(audio_path, "rb") as audio_file:
        transcript = client.audio.transcriptions.create(
            model=AUDIO_MODEL,
            file=audio_file,
            response_format="verbose_json",
            timestamp_granularities=["segment"],
        )
    segments = transcript.segments
    print(f"听写完成！共提取出 {len(segments)} 句解说词。")
    return segments


def extract_keyframes(video_path, segments, output_dir):
    """在每句解说词的中间时刻抽取一帧作为候选关键帧"""
    print("正在抽取候选画面...")
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)

    extracted_data = []
    for i, segment in enumerate(segments):
        mid_time = (segment.start + segment.end) / 2
        frame_number = int(mid_time * fps)

        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
        ret, frame = cap.read()

        if ret:
            image_filename = f"frame_{i}.jpg"
            image_path = os.path.join(output_dir, image_filename)
            cv2.imwrite(image_path, frame)
            extracted_data.append({
                "id": i,
                "text": segment.text,
                "image_path": image_path,
                "image_filename": image_filename,
            })

    cap.release()
    print(f"成功抽取 {len(extracted_data)} 张候选截图！")
    return extracted_data


def generate_tutorial(client, extracted_data):
    """将转录文本和关键帧发送给视觉大模型，生成图文教程"""
    print(f"正在呼叫模型 {VISION_MODEL} 进行全局思考与排版，请稍候...")

    system_prompt = """
你是一个世界级的产品体验与技术文档专家。
我现在会给你提供一个操作视频的完整解说词片段，以及每一句话对应的视频截图候选。

你的任务是：统揽全局，将这些碎片信息转化为一篇极具专业感、步骤清晰的图文操作指南。

【核心要求】：
1. 语义过滤：讲师会有废话（如"呃、接下来我们看"），请直接忽略，只提取"操作动词"。
2. 画面优选：如果连续几张截图画面没有变化，或者讲师在长篇大论，请将它们合并为一个步骤，并只挑选最能体现操作结果的那一张图片。
3. 精准定位提示：在描述步骤时，请发挥你强大的视觉能力，明确指出目标按钮的位置（例如："点击页面右上角的蓝色【保存】按钮"），引导用户的视线。
4. 输出格式：请使用优美的 Markdown 格式。引用图片时，请使用对应的文件名（如：![步骤1说明](frame_2.jpg)）。
"""

    user_content = [{"type": "text", "text": "以下是按照时间顺序提供的视频片段数据："}]
    for data in extracted_data:
        user_content.append({
            "type": "text",
            "text": f"\n--- 片段 {data['id']} ---\n解说词：{data['text']}\n对应的候选截图：",
        })
        base64_image = encode_image(data["image_path"])
        user_content.append({
            "type": "image_url",
            "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
        })

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_content},
    ]

    response = client.chat.completions.create(
        model=VISION_MODEL,
        messages=messages,
        max_tokens=MAX_TOKENS,
        temperature=TEMPERATURE,
    )
    return response.choices[0].message.content


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    client = OpenAI(api_key=API_KEY, base_url=API_BASE_URL)

    # 1. 提取音频
    extract_audio(VIDEO_PATH, AUDIO_PATH)

    # 2. 语音转文字
    segments = transcribe_audio(client, AUDIO_PATH)

    # 3. 抽取关键帧
    extracted_data = extract_keyframes(VIDEO_PATH, segments, OUTPUT_DIR)

    # 4. 大模型生成图文教程
    final_markdown = generate_tutorial(client, extracted_data)

    # 5. 写入输出文件
    md_path = os.path.join(OUTPUT_DIR, "Ultimate_Tutorial.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(final_markdown)

    print(f"\n运行成功！请查看 {OUTPUT_DIR}/Ultimate_Tutorial.md")


if __name__ == "__main__":
    main()
