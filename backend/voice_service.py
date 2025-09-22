import requests
import json
import base64
import io
import os
from typing import Optional
import asyncio

class VoiceService:
    def __init__(self):
        # 使用七牛云的语音服务（从环境变量读取配置）
        self.base_url = os.getenv("QINIU_BASE_URL", "https://openai.qiniu.com/v1")
        self.api_key = os.getenv("QINIU_TTS_KEY", "")
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}" if self.api_key else ""
        }
        
        # 缓存音色类型
        self._voice_type = None
    
    async def _get_voice_type(self) -> str:
        """获取可用的音色类型"""
        if self._voice_type:
            return self._voice_type
            
        try:
            if not self.api_key:
                raise RuntimeError("缺少QINIU_TTS_KEY，请在环境变量中配置")
            response = requests.get(f"{self.base_url}/voice/list", headers=self.headers, timeout=30)
            response.raise_for_status()
            voices = response.json()
            
            # 优先选择包含"zh"的中文音色
            for voice in voices:
                if "zh" in voice.get("voice_type", ""):
                    self._voice_type = voice["voice_type"]
                    return self._voice_type
            
            # 如果没有中文音色，使用第一个
            if voices:
                self._voice_type = voices[0]["voice_type"]
                return self._voice_type
                
        except Exception as e:
            print(f"获取音色列表失败: {e}")
            
        # 默认音色
        self._voice_type = "zh-CN-XiaoxiaoNeural"
        return self._voice_type
    
    async def speech_to_text(self, audio_data: bytes) -> str:
        """语音转文字 - 使用七牛云ASR"""
        try:
            if not self.api_key:
                return "ASR配置缺失：请设置环境变量QINIU_TTS_KEY"
            # 将音频数据转换为base64
            audio_b64 = base64.b64encode(audio_data).decode('utf-8')
            
            payload = {
                "model": "asr",
                "audio": {
                    "format": "mp3",
                    "data": audio_b64
                }
            }
            
            response = requests.post(
                f"{self.base_url}/voice/asr",
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                text = result.get("data", {}).get("result", {}).get("text", "")
                return text if text else "未能识别到语音内容"
            else:
                print(f"ASR API错误: {response.status_code} - {response.text}")
                return "语音识别服务暂时不可用"
                
        except Exception as e:
            print(f"语音识别出错: {str(e)}")
            return f"语音识别出错: {str(e)}"
    
    async def text_to_speech(self, text: str, voice_type: str = None) -> bytes:
        """文字转语音 - 使用七牛云TTS"""
        try:
            if not self.api_key:
                raise RuntimeError("TTS配置缺失：请设置环境变量QINIU_TTS_KEY")
            if not voice_type:
                voice_type = await self._get_voice_type()
            
            payload = {
                "audio": {
                    "voice_type": voice_type,
                    "encoding": "mp3",
                    "speed_ratio": 1.0
                },
                "request": {
                    "text": text
                }
            }
            
            response = requests.post(
                f"{self.base_url}/voice/tts",
                headers=self.headers,
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                audio_b64 = result.get("data")
                if audio_b64:
                    return base64.b64decode(audio_b64)
                else:
                    raise RuntimeError(f"响应不含音频数据: {result}")
            else:
                print(f"TTS API错误: {response.status_code} - {response.text}")
                raise RuntimeError(f"TTS服务错误: {response.status_code}")
                
        except Exception as e:
            print(f"文字转语音出错: {str(e)}")
            raise e
    
    async def process_voice_chat(self, audio_data: bytes, character_name: str = "助手") -> dict:
        """处理语音聊天 - 包含ASR和TTS的完整流程"""
        try:
            # 1. 语音转文字
            user_text = await self.speech_to_text(audio_data)
            if not user_text or "出错" in user_text:
                return {
                    "success": False,
                    "error": user_text,
                    "user_text": "",
                    "response_text": "",
                    "response_audio": None
                }
            
            # 2. 这里应该调用AI服务生成回复
            # 暂时返回模拟回复
            response_text = f"我听到了您说：{user_text}。这是来自{character_name}的回复。"
            
            # 3. 文字转语音
            response_audio = await self.text_to_speech(response_text)
            
            return {
                "success": True,
                "user_text": user_text,
                "response_text": response_text,
                "response_audio": base64.b64encode(response_audio).decode('utf-8')
            }
            
        except Exception as e:
            print(f"语音聊天处理出错: {str(e)}")
            return {
                "success": False,
                "error": f"语音聊天处理出错: {str(e)}",
                "user_text": "",
                "response_text": "",
                "response_audio": None
            }