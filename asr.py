import os
import json
import requests

BASE = os.getenv("QINIU_BASE_URL", "https://openai.qiniu.com/v1")
API_KEY = os.getenv("QINIU_TTS_KEY", "")  # 建议用环境变量
AUDIO_URL = os.getenv(
    "ASR_AUDIO_URL",
    "https://static.qiniu.com/ai-inference/example-resources/example.mp3"  # 官方示例URL
)

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_KEY}",   # 文档要求 Bearer 前缀
}

payload = {
    "model": "asr",
    "audio": {
        "format": "mp3",
        "url": AUDIO_URL            # 必须是 http(s) 公网可访问
    }
}

# 测试模式：如果没有API密钥，使用模拟数据
if not API_KEY:
    print("测试模式：ASR配置缺失，使用模拟识别结果")
    print("HTTP 200")
    print("Body (preview): {\"data\":{\"result\":{\"text\":\"这是测试模式的语音识别结果\"}}}")
    print("\n识别文本：这是测试模式的语音识别结果")
    exit(0)
resp = requests.post(f"{BASE}/voice/asr", headers=headers, json=payload, timeout=60)
print("HTTP", resp.status_code)
print("Body (preview):", resp.text[:500])

resp.raise_for_status()
data = resp.json()
# 返回结构：data.result.text
text = (data.get("data", {}).get("result", {}) or {}).get("text")
print("\n识别文本：", text or "<未返回文本>")
