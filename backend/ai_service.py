import requests
import json
import asyncio
from typing import Dict, Any, List
import os

class AIService:
    def __init__(self):
        # 从环境变量读取，避免将密钥硬编码进仓库
        self.api_key = os.getenv("ALIBABA_CLOUD_API_KEY", "")
        self.base_url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
        self.model = "qwen-max"
        
    async def chat_with_character(self, character: Dict[str, Any], user_message: str) -> str:
        """与AI角色进行对话"""
        # 构建角色提示词
        system_prompt = self._build_character_prompt(character)
        
        # 构建消息
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]
        
        # 调用阿里云百炼API
        response = await self._call_qwen_api(messages)
        return response
    
    def _build_character_prompt(self, character: Dict[str, Any]) -> str:
        """构建角色提示词"""
        prompt = f"""你是{character['name']}，{character['description']}

角色设定：
- 性格特点：{character['personality']}
- 说话风格：{character['speaking_style']}
- 知识背景：{character['knowledge']}
- 特殊技能：{', '.join(character['skills'])}

请严格按照角色设定进行对话，保持角色的独特性和一致性。你的回答应该：
1. 符合角色的性格和说话风格
2. 体现角色的知识背景
3. 保持对话的自然流畅
4. 适当使用角色的特殊技能
5. 语言生动有趣，富有感染力
6. 适当使用角色相关的专业术语或表达方式

记住，你就是{character['name']}本人，请以第一人称进行对话。让对话充满活力和个性！"""
        
        return prompt
    
    async def _call_qwen_api(self, messages: List[Dict[str, str]]) -> str:
        """调用通义千问API"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.model,
            "input": {
                "messages": messages
            },
            "parameters": {
                "temperature": 0.8,
                "top_p": 0.9,
                "max_tokens": 1000
            }
        }
        
        try:
            response = requests.post(
                self.base_url,
                headers=headers,
                json=data,
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            if "output" in result and "text" in result["output"]:
                return result["output"]["text"]
            else:
                return "抱歉，我现在无法回应，请稍后再试。"
                
        except Exception as e:
            print(f"API调用错误: {e}")
            return "抱歉，我现在无法回应，请稍后再试。"
    
    async def generate_story(self, character: Dict[str, Any], topic: str) -> str:
        """生成角色相关的故事"""
        system_prompt = f"""你是{character['name']}，现在需要根据主题"{topic}"创作一个故事。

请以你的角色身份和视角来创作这个故事，体现你的：
- 性格特点：{character['personality']}
- 知识背景：{character['knowledge']}
- 创作风格：{character.get('writing_style', '生动有趣')}

故事要求：
1. 长度适中（200-500字）
2. 情节完整，有起承转合
3. 体现角色的独特视角
4. 语言生动，富有感染力"""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"请创作一个关于{topic}的故事"}
        ]
        
        return await self._call_qwen_api(messages)
    
    async def give_advice(self, character: Dict[str, Any], problem: str) -> str:
        """基于角色背景给出建议"""
        system_prompt = f"""你是{character['name']}，现在有人向你寻求建议。

请基于你的：
- 人生经历：{character['knowledge']}
- 智慧观点：{character['personality']}
- 专业领域：{character.get('expertise', '人生智慧')}

给出真诚、有深度的建议。你的建议应该：
1. 体现你的独特视角和智慧
2. 实用且具有启发性
3. 语言温暖，富有同理心
4. 结合你的经历给出具体指导"""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"我遇到了这样的问题：{problem}，请给我一些建议"}
        ]
        
        return await self._call_qwen_api(messages)
    
    async def answer_question(self, character: Dict[str, Any], question: str) -> str:
        """回答基于角色知识的问题"""
        system_prompt = f"""你是{character['name']}，现在有人向你提问。

请基于你的专业知识：
- 知识领域：{character['knowledge']}
- 专业背景：{character.get('expertise', '')}
- 独特见解：{character['personality']}

给出准确、深入的答案。你的回答应该：
1. 体现你的专业水平
2. 语言清晰易懂
3. 包含具体的例子或解释
4. 保持角色的说话风格"""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question}
        ]
        
        return await self._call_qwen_api(messages)
