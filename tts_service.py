import edge_tts
import asyncio
import os
import uuid

# 确保保存目录存在
OUTPUT_DIR = "static/audio"
os.makedirs(OUTPUT_DIR, exist_ok=True)

async def text_to_speech(text: str) -> str:
    """
    将文本转换为语音，返回文件路径
    voice: zh-CN-YunxiNeural (男声，适合新闻/政治)
    """
    voice = "zh-CN-YunxiNeural" 
    filename = f"{uuid.uuid4()}.mp3"
    output_path = os.path.join(OUTPUT_DIR, filename)
    
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_path)
    
    return f"/static/audio/{filename}"