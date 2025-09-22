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
    if not API_KEY:
        raise RuntimeError("缺少QINIU_TTS_KEY环境变量")
    r = requests.post(f"{BASE}/voice/tts", headers=HEADERS, json=payload, timeout=60)
    # 不直接 raise，先看返回体里有没有错误信息
    if r.status_code >= 400:
        print("HTTP", r.status_code, r.text[:500])
        r.raise_for_status()
    # 文档说明：返回 JSON，data 字段是 base64 音频。:contentReference[oaicite:2]{index=2}
    j = r.json()
    audio_b64 = j.get("data")
    if not audio_b64:
        raise RuntimeError(f"响应不含音频数据: {j}")
    with open(outfile, "wb") as f:
        f.write(base64.b64decode(audio_b64))
    print(f"已保存音频：{outfile}，时长(毫秒)：{j.get('addition',{}).get('duration')}")

if __name__ == "__main__":
    if not API_KEY:
        raise SystemExit("请先设置环境变量 QINIU_TTS_KEY=sk-xxxx")
    voice = pick_voice()
    if not voice:
        raise SystemExit("没有获取到可用音色，请检查鉴权或改用备用域名 https://api.qnaigc.com/v1 。")
    print("使用音色：", voice)
    tts("你好，世界！这是七牛云 TTS 的 Python 测试。", voice, outfile="tts_out.mp3")
