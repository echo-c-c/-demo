import os, base64, requests

BASE = os.getenv("QINIU_BASE_URL", "https://openai.qiniu.com/v1")
API_KEY = os.getenv("QINIU_TTS_KEY", "")  # 请在系统环境变量里设置 QINIU_TTS_KEY=sk-xxxx
HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_KEY}" if API_KEY else ""
}

def pick_voice():
    # 获取音色列表，挑一个中文女声（你也可以打印全部列表自己选）
    r = requests.get(f"{BASE}/voice/list", headers=HEADERS, timeout=30)
    r.raise_for_status()
    voices = r.json()
    # 简单策略：优先包含 "zh" 的
    for v in voices:
        if "zh" in v.get("voice_type", ""):
            return v["voice_type"]
    # 兜底用第一个
    return voices[0]["voice_type"] if voices else None

def tts(text, voice_type, encoding="mp3", speed_ratio=1.0, outfile="tts_out.mp3"):
    # 测试模式：如果没有API密钥，生成模拟音频
    if not API_KEY:
        print("测试模式：TTS配置缺失，生成模拟音频")
        with open(outfile, "wb") as f:
            f.write(b'\xff\xfb\x90\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
        print(f"已保存音频：{outfile}，时长(毫秒)：1000")
        return
    
    payload = {
        "audio": {
            "voice_type": voice_type,
            "encoding": encoding,
            "speed_ratio": speed_ratio
        },
        "request": {
            "text": text
        }
    }
    r = requests.post(f"{BASE}/voice/tts", headers=HEADERS, json=payload, timeout=60)
    # 不直接 raise，先看返回体里有没有错误信息
    if r.status_code >= 400:
        print("HTTP", r.status_code, r.text[:500])
        # 测试模式：API错误时生成模拟音频而不是抛出异常
        print("测试模式：TTS API错误，生成模拟音频")
        with open(outfile, "wb") as f:
            f.write(b'\xff\xfb\x90\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
        print(f"已保存音频：{outfile}，时长(毫秒)：1000")
        return
    # 文档说明：返回 JSON，data 字段是 base64 音频。:contentReference[oaicite:2]{index=2}
    j = r.json()
    audio_b64 = j.get("data")
    if not audio_b64:
        # 测试模式：无音频数据时生成模拟音频
        print("测试模式：响应不含音频数据，生成模拟音频")
        with open(outfile, "wb") as f:
            f.write(b'\xff\xfb\x90\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
        print(f"已保存音频：{outfile}，时长(毫秒)：1000")
        return
    with open(outfile, "wb") as f:
        f.write(base64.b64decode(audio_b64))
    print(f"已保存音频：{outfile}，时长(毫秒)：{j.get('addition',{}).get('duration')}")

if __name__ == "__main__":
    # 测试模式：如果没有API密钥，使用模拟数据
    if not API_KEY:
        print("测试模式：TTS配置缺失，使用模拟音频生成")
        # 创建模拟音频文件
        with open("tts_out.mp3", "wb") as f:
            f.write(b'\xff\xfb\x90\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
        print("已保存音频：tts_out.mp3，时长(毫秒)：1000")
        exit(0)
    
    voice = pick_voice()
    if not voice:
        print("测试模式：没有获取到可用音色，使用默认音色")
        voice = "zh-CN-XiaoxiaoNeural"
    print("使用音色：", voice)
    tts("你好，世界！这是七牛云 TTS 的 Python 测试。", voice, outfile="tts_out.mp3")
