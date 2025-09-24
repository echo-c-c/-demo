import json
from typing import Dict, Any, List, Optional
from ai_service import AIService

class CharacterManager:
    def __init__(self):
        self.characters = {}
        self.ai_service = AIService()
        self.init_characters()
    
    def init_characters(self):
        """初始化角色数据"""
        self.characters = {
            "harry_potter": {
                "id": "harry_potter",
                "name": "哈利波特",
                "description": "来自魔法世界的年轻巫师，勇敢、善良，拥有强大的魔法天赋",
                "personality": "勇敢、正义、善良、有时冲动，对朋友忠诚",
                "speaking_style": "年轻、直接、有时会使用魔法术语",
                "knowledge": "霍格沃茨魔法学校的学生，精通各种魔法咒语和魔法史",
                "skills": ["魔法知识", "故事创作", "人生建议", "问答解惑"],
                "expertise": "魔法、友谊、勇气",
                "writing_style": "充满想象力和魔法色彩",
                "avatar": "/static/images/characters/harry_potter.jpg",
                "voice": "xiaoyun",
                "category": "文学角色"
            },
            "socrates": {
                "id": "socrates",
                "name": "苏格拉底",
                "description": "古希腊哲学家，以苏格拉底式问答法闻名，追求真理和智慧",
                "personality": "智慧、谦逊、善于提问、追求真理",
                "speaking_style": "哲学思辨、善于反问、语言深刻",
                "knowledge": "古希腊哲学、伦理学、认识论、辩证法",
                "skills": ["哲学思辨", "智慧建议", "深度问答", "逻辑推理"],
                "expertise": "哲学、智慧、道德",
                "writing_style": "深刻、思辨、富有哲理",
                "avatar": "/static/images/characters/socrates.jpg",
                "voice": "xiaogang",
                "category": "历史人物"
            },
            "einstein": {
                "id": "einstein",
                "name": "爱因斯坦",
                "description": "伟大的物理学家，相对论的创立者，对科学和人类思想有深远影响",
                "personality": "智慧、幽默、富有想象力、热爱科学",
                "speaking_style": "科学严谨、富有想象力、语言生动",
                "knowledge": "物理学、数学、相对论、量子力学、科学哲学",
                "skills": ["科学解释", "创新思维", "教育指导", "哲学思考"],
                "expertise": "物理学、科学、创新",
                "writing_style": "科学严谨、富有想象力",
                "avatar": "/static/images/characters/einstein.jpg",
                "voice": "xiaofeng",
                "category": "科学家"
            },
            "shakespeare": {
                "id": "shakespeare",
                "name": "莎士比亚",
                "description": "英国文学巨匠，戏剧大师，创作了众多经典作品",
                "personality": "才华横溢、情感丰富、观察敏锐、语言优美",
                "speaking_style": "文学化、富有诗意、情感丰富",
                "knowledge": "英国文学、戏剧、诗歌、人性分析",
                "skills": ["文学创作", "情感分析", "语言艺术", "人生感悟"],
                "expertise": "文学、戏剧、人性",
                "writing_style": "诗意、深刻、富有感染力",
                "avatar": "/static/images/characters/shakespeare.jpg",
                "voice": "xiaogang",
                "category": "文学家"
            },
            "leonardo_da_vinci": {
                "id": "leonardo_da_vinci",
                "name": "达芬奇",
                "description": "文艺复兴时期的全才，画家、发明家、科学家、工程师",
                "personality": "好奇心强、多才多艺、观察敏锐、富有创造力",
                "speaking_style": "博学、富有创造力、语言生动",
                "knowledge": "艺术、科学、工程、解剖学、机械学",
                "skills": ["艺术指导", "科学解释", "创新设计", "观察分析"],
                "expertise": "艺术、科学、创新",
                "writing_style": "生动、富有创造力",
                "avatar": "/static/images/characters/leonardo_da_vinci.jpg",
                "voice": "xiaofeng",
                "category": "艺术家"
            }
        }
    
    def get_all_characters(self) -> List[Dict[str, Any]]:
        """获取所有角色"""
        return list(self.characters.values())
    
    def get_character(self, character_id: str) -> Optional[Dict[str, Any]]:
        """获取特定角色"""
        return self.characters.get(character_id)
    
    def search_characters(self, query: str) -> List[Dict[str, Any]]:
        """搜索角色"""
        query = query.lower()
        results = []
        
        for character in self.characters.values():
            if (query in character["name"].lower() or 
                query in character["description"].lower() or
                query in character["category"].lower() or
                any(query in skill.lower() for skill in character["skills"])):
                results.append(character)
        
        return results
    
    async def use_skill(self, character_id: str, skill_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """使用角色技能"""
        character = self.get_character(character_id)
        if not character:
            return {"error": "角色不存在"}
        
        if skill_name not in character["skills"]:
            return {"error": "角色不具备此技能"}
        
        try:
            if skill_name == "魔法知识":
                question = params.get("question", "请介绍一下魔法世界的基础知识")
                response = await self.ai_service.chat_with_character(
                    character,
                    f"作为魔法专家，请回答：{question}"
                )
                return {
                    "skill": skill_name,
                    "result": response,
                    "character": character["name"]
                }
            
            elif skill_name == "故事创作":
                topic = params.get("topic", "冒险")
                story = await self.ai_service.generate_story(character, topic)
                return {
                    "skill": skill_name,
                    "result": story,
                    "character": character["name"]
                }
            
            elif skill_name == "人生建议":
                problem = params.get("problem", "")
                advice = await self.ai_service.give_advice(character, problem)
                return {
                    "skill": skill_name,
                    "result": advice,
                    "character": character["name"]
                }
            
            elif skill_name in ["问答解惑", "深度问答", "科学解释"]:
                question = params.get("question", "")
                answer = await self.ai_service.answer_question(character, question)
                return {
                    "skill": skill_name,
                    "result": answer,
                    "character": character["name"]
                }
            
            elif skill_name == "哲学思辨":
                topic = params.get("topic", "")
                response = await self.ai_service.chat_with_character(
                    character, 
                    f"请对'{topic}'这个话题进行哲学思辨"
                )
                return {
                    "skill": skill_name,
                    "result": response,
                    "character": character["name"]
                }
            
            elif skill_name == "创新思维":
                challenge = params.get("challenge", "")
                response = await self.ai_service.chat_with_character(
                    character,
                    f"面对这个挑战：'{challenge}'，请提供创新性的解决方案"
                )
                return {
                    "skill": skill_name,
                    "result": response,
                    "character": character["name"]
                }
            
            elif skill_name == "情感分析":
                situation = params.get("situation", "")
                response = await self.ai_service.chat_with_character(
                    character,
                    f"请分析这个情感状况：'{situation}'"
                )
                return {
                    "skill": skill_name,
                    "result": response,
                    "character": character["name"]
                }
            
            elif skill_name == "文学创作":
                topic = params.get("topic", "人生感悟")
                response = await self.ai_service.chat_with_character(
                    character,
                    f"请创作一个关于'{topic}'的文学作品"
                )
                return {
                    "skill": skill_name,
                    "result": response,
                    "character": character["name"]
                }
            
            elif skill_name == "语言艺术":
                text = params.get("text", "")
                response = await self.ai_service.chat_with_character(
                    character,
                    f"请用优美的语言艺术来润色这段文字：'{text}'"
                )
                return {
                    "skill": skill_name,
                    "result": response,
                    "character": character["name"]
                }
            
            elif skill_name == "人生感悟":
                experience = params.get("experience", "")
                response = await self.ai_service.chat_with_character(
                    character,
                    f"基于这个经历：'{experience}'，请分享你的人生感悟"
                )
                return {
                    "skill": skill_name,
                    "result": response,
                    "character": character["name"]
                }
            
            elif skill_name == "艺术指导":
                art_type = params.get("art_type", "绘画")
                response = await self.ai_service.chat_with_character(
                    character,
                    f"请提供关于'{art_type}'的艺术指导"
                )
                return {
                    "skill": skill_name,
                    "result": response,
                    "character": character["name"]
                }
            
            elif skill_name == "创新设计":
                design_challenge = params.get("design_challenge", "")
                response = await self.ai_service.chat_with_character(
                    character,
                    f"请为这个设计挑战提供创新方案：'{design_challenge}'"
                )
                return {
                    "skill": skill_name,
                    "result": response,
                    "character": character["name"]
                }
            
            elif skill_name == "观察分析":
                observation = params.get("observation", "")
                response = await self.ai_service.chat_with_character(
                    character,
                    f"请分析这个观察：'{observation}'"
                )
                return {
                    "skill": skill_name,
                    "result": response,
                    "character": character["name"]
                }
            
            elif skill_name == "教育指导":
                subject = params.get("subject", "科学")
                response = await self.ai_service.chat_with_character(
                    character,
                    f"请提供关于'{subject}'的教育指导"
                )
                return {
                    "skill": skill_name,
                    "result": response,
                    "character": character["name"]
                }
            
            elif skill_name == "哲学思考":
                philosophical_question = params.get("philosophical_question", "")
                response = await self.ai_service.chat_with_character(
                    character,
                    f"请从哲学角度思考这个问题：'{philosophical_question}'"
                )
                return {
                    "skill": skill_name,
                    "result": response,
                    "character": character["name"]
                }
            
            elif skill_name == "逻辑推理":
                logical_problem = params.get("logical_problem", "")
                response = await self.ai_service.chat_with_character(
                    character,
                    f"请用逻辑推理来解决这个问题：'{logical_problem}'"
                )
                return {
                    "skill": skill_name,
                    "result": response,
                    "character": character["name"]
                }
            
            else:
                return {"error": "技能暂未实现"}
                
        except Exception as e:
            return {"error": f"技能使用失败: {str(e)}"}
    
    def get_character_skills(self, character_id: str) -> List[str]:
        """获取角色技能列表"""
        character = self.get_character(character_id)
        if character:
            return character["skills"]
        return []
    
    def get_characters_by_category(self, category: str) -> List[Dict[str, Any]]:
        """按分类获取角色"""
        return [
            character for character in self.characters.values()
            if character["category"] == category
        ]
    
    def get_character_categories(self) -> List[str]:
        """获取所有角色分类"""
        categories = set()
        for character in self.characters.values():
            categories.add(character["category"])
        return list(categories)
