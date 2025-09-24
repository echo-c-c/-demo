from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, UploadFile, File, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import uvicorn
import json
import asyncio
from typing import List, Dict, Any, Optional
import sqlite3
import os
from datetime import datetime
import base64
import io
from pydantic import BaseModel
from dotenv import load_dotenv

# 加载环境变量
load_dotenv('../.env')

from ai_service import AIService
from voice_service import VoiceService
from database import DatabaseManager
from character_manager import CharacterManager
from auth_service import AuthService

app = FastAPI(title="时光对话者 - TimeTalker", version="1.0.0")

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化服务
ai_service = AIService()
voice_service = VoiceService()
db_manager = DatabaseManager()
character_manager = CharacterManager()
auth_service = AuthService()

# 安全配置
security = HTTPBearer()

# Pydantic模型
class UserRegister(BaseModel):
    username: str
    email: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class UserProfile(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    avatar_url: Optional[str] = None

class PasswordChange(BaseModel):
    old_password: str
    new_password: str

# 依赖项
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """获取当前用户"""
    token = credentials.credentials
    user_info = auth_service.verify_token(token)
    if not user_info:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证令牌",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user_info

# 存储活跃的WebSocket连接
active_connections: List[WebSocket] = []

@app.on_event("startup")
async def startup_event():
    """应用启动时初始化数据库"""
    db_manager.init_database()
    character_manager.init_characters()

# 静态文件服务
app.mount("/static", StaticFiles(directory="../frontend"), name="static")

@app.get("/")
async def root():
    """根路径，返回前端页面"""
    import os
    frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend", "index.html")
    if os.path.exists(frontend_path):
        return FileResponse(frontend_path)
    else:
        return HTMLResponse(content="<h1>前端文件未找到</h1><p>请检查frontend/index.html文件是否存在</p>", status_code=404)

@app.get("/test")
async def test_page():
    """测试页面"""
    import os
    test_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "test.html")
    if os.path.exists(test_path):
        return FileResponse(test_path)
    else:
        return HTMLResponse(content="<h1>测试页面未找到</h1>", status_code=404)

# 认证相关接口
@app.post("/api/auth/register")
async def register(user_data: UserRegister):
    """用户注册"""
    result = auth_service.create_user(
        username=user_data.username,
        email=user_data.email,
        password=user_data.password
    )
    if result["success"]:
        return result
    else:
        raise HTTPException(status_code=400, detail=result["message"])

@app.post("/api/auth/login")
async def login(user_data: UserLogin):
    """用户登录"""
    result = auth_service.authenticate_user(
        username=user_data.username,
        password=user_data.password
    )
    if result["success"]:
        return result
    else:
        raise HTTPException(status_code=401, detail=result["message"])

@app.get("/api/auth/me")
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """获取当前用户信息"""
    user_info = auth_service.get_user_by_id(current_user["user_id"])
    if user_info:
        return {"success": True, "user": user_info}
    else:
        raise HTTPException(status_code=404, detail="用户不存在")

@app.put("/api/auth/profile")
async def update_profile(profile_data: UserProfile, current_user: dict = Depends(get_current_user)):
    """更新用户资料"""
    update_data = {k: v for k, v in profile_data.dict().items() if v is not None}
    result = auth_service.update_user_profile(current_user["user_id"], **update_data)
    if result["success"]:
        return result
    else:
        raise HTTPException(status_code=400, detail=result["message"])

@app.post("/api/auth/change-password")
async def change_password(password_data: PasswordChange, current_user: dict = Depends(get_current_user)):
    """修改密码"""
    result = auth_service.change_password(
        user_id=current_user["user_id"],
        old_password=password_data.old_password,
        new_password=password_data.new_password
    )
    if result["success"]:
        return result
    else:
        raise HTTPException(status_code=400, detail=result["message"])

@app.delete("/api/auth/deactivate")
async def deactivate_account(current_user: dict = Depends(get_current_user)):
    """停用账户"""
    result = auth_service.deactivate_user(current_user["user_id"])
    if result["success"]:
        return result
    else:
        raise HTTPException(status_code=400, detail=result["message"])

@app.get("/api/characters")
async def get_characters():
    """获取所有可用角色"""
    return character_manager.get_all_characters()

@app.get("/api/characters/search")
async def search_characters(query: str):
    """搜索角色"""
    return character_manager.search_characters(query)

@app.get("/api/characters/{character_id}")
async def get_character(character_id: str):
    """获取特定角色信息"""
    character = character_manager.get_character(character_id)
    if not character:
        raise HTTPException(status_code=404, detail="角色不存在")
    return character

@app.post("/api/chat/text")
async def chat_text(request: dict, current_user: dict = Depends(get_current_user)):
    """文本聊天接口"""
    character_id = request.get("character_id")
    message = request.get("message")
    
    if not character_id or not message:
        raise HTTPException(status_code=400, detail="缺少必要参数")
    
    character = character_manager.get_character(character_id)
    if not character:
        raise HTTPException(status_code=404, detail="角色不存在")
    
    response = await ai_service.chat_with_character(character, message)
    
    # 保存聊天记录（关联用户ID）
    user_id = str(current_user["user_id"])
    db_manager.save_chat_record(character_id, "user", message, "text", user_id)
    db_manager.save_chat_record(character_id, "assistant", response, "text", user_id)
    
    return {"response": response}

@app.post("/api/chat/voice")
async def chat_voice(character_id: str, audio_file: UploadFile = File(...)):
    """语音聊天接口"""
    character = character_manager.get_character(character_id)
    if not character:
        raise HTTPException(status_code=404, detail="角色不存在")
    
    # 读取音频文件
    audio_data = await audio_file.read()
    
    # 语音识别
    text = await voice_service.speech_to_text(audio_data)
    
    # AI对话
    response = await ai_service.chat_with_character(character, text)
    
    # 文本转语音
    audio_response = await voice_service.text_to_speech(response)
    
    # 保存聊天记录
    db_manager.save_chat_record(character_id, "user", text, "voice")
    db_manager.save_chat_record(character_id, "assistant", response, "voice")
    
    return {
        "text": text,
        "response": response,
        "audio": base64.b64encode(audio_response).decode('utf-8')
    }

@app.websocket("/ws/{character_id}")
async def websocket_endpoint(websocket: WebSocket, character_id: str):
    """WebSocket实时聊天"""
    await websocket.accept()
    active_connections.append(websocket)
    
    character = character_manager.get_character(character_id)
    if not character:
        await websocket.close(code=1008, reason="角色不存在")
        return
    
    try:
        while True:
            # 接收消息
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            if message_data["type"] == "text":
                # 文本消息
                response = await ai_service.chat_with_character(character, message_data["content"])
                await websocket.send_text(json.dumps({
                    "type": "text",
                    "content": response,
                    "timestamp": datetime.now().isoformat()
                }))
            
            elif message_data["type"] == "voice":
                # 语音消息
                try:
                    audio_data = base64.b64decode(message_data["audio"])
                    voice_result = await voice_service.process_voice_chat(audio_data, character["name"])
                    
                    if voice_result["success"]:
                        # 使用AI服务生成回复
                        ai_response = await ai_service.chat_with_character(character, voice_result["user_text"])
                        
                        # 将AI回复转换为语音
                        response_audio = await voice_service.text_to_speech(ai_response)
                        
                        await websocket.send_text(json.dumps({
                            "type": "voice_response",
                            "user_text": voice_result["user_text"],
                            "response_text": ai_response,
                            "response_audio": base64.b64encode(response_audio).decode('utf-8'),
                            "timestamp": datetime.now().isoformat()
                        }))
                    else:
                        await websocket.send_text(json.dumps({
                            "type": "error",
                            "content": voice_result["error"],
                            "timestamp": datetime.now().isoformat()
                        }))
                        
                except Exception as e:
                    await websocket.send_text(json.dumps({
                        "type": "error",
                        "content": f"语音处理出错: {str(e)}",
                        "timestamp": datetime.now().isoformat()
                    }))
            
    
    except WebSocketDisconnect:
        active_connections.remove(websocket)

@app.get("/api/chat/history/{character_id}")
async def get_chat_history(character_id: str, limit: int = 50, current_user: dict = Depends(get_current_user)):
    """获取聊天历史"""
    user_id = str(current_user["user_id"])
    return db_manager.get_chat_history(character_id, limit, user_id)

@app.get("/api/chat/history")
async def get_user_chat_history(current_user: dict = Depends(get_current_user)):
    """获取用户所有聊天历史"""
    user_id = str(current_user["user_id"])
    return db_manager.get_user_chat_history(user_id)

@app.delete("/api/chat/history/{character_id}")
async def clear_chat_history(character_id: str, current_user: dict = Depends(get_current_user)):
    """清空与特定角色的聊天历史"""
    user_id = str(current_user["user_id"])
    return db_manager.clear_chat_history(character_id, user_id)

@app.get("/api/chat/search")
async def search_chat_history(query: str, current_user: dict = Depends(get_current_user)):
    """搜索聊天历史"""
    user_id = str(current_user["user_id"])
    return db_manager.search_chat_history(query, user_id)

# 角色收藏相关接口
@app.post("/api/characters/{character_id}/favorite")
async def add_favorite_character(character_id: str, current_user: dict = Depends(get_current_user)):
    """添加角色到收藏"""
    user_id = str(current_user["user_id"])
    return db_manager.add_favorite_character(user_id, character_id)

@app.delete("/api/characters/{character_id}/favorite")
async def remove_favorite_character(character_id: str, current_user: dict = Depends(get_current_user)):
    """从收藏中移除角色"""
    user_id = str(current_user["user_id"])
    return db_manager.remove_favorite_character(user_id, character_id)

@app.get("/api/user/favorites")
async def get_favorite_characters(current_user: dict = Depends(get_current_user)):
    """获取用户收藏的角色列表"""
    user_id = str(current_user["user_id"])
    favorite_ids = db_manager.get_favorite_characters(user_id)
    
    # 获取完整的角色信息
    favorite_characters = []
    for character_id in favorite_ids:
        character = character_manager.get_character(character_id)
        if character:
            character["is_favorited"] = True
            favorite_characters.append(character)
    
    return {"favorites": favorite_characters}

@app.get("/api/characters/{character_id}/favorite-status")
async def get_favorite_status(character_id: str, current_user: dict = Depends(get_current_user)):
    """检查角色收藏状态"""
    user_id = str(current_user["user_id"])
    is_favorited = db_manager.is_character_favorited(user_id, character_id)
    return {"is_favorited": is_favorited}

# 用户设置相关接口
@app.post("/api/user/settings")
async def save_user_settings(settings: dict, current_user: dict = Depends(get_current_user)):
    """保存用户设置"""
    user_id = str(current_user["user_id"])
    results = []
    
    for key, value in settings.items():
        result = db_manager.save_user_setting(user_id, key, str(value))
        results.append(result)
    
    return {"results": results}

@app.get("/api/user/settings")
async def get_user_settings(current_user: dict = Depends(get_current_user)):
    """获取用户设置"""
    user_id = str(current_user["user_id"])
    settings = db_manager.get_all_user_settings(user_id)
    return {"settings": settings}

@app.get("/api/user/settings/{setting_key}")
async def get_user_setting(setting_key: str, current_user: dict = Depends(get_current_user)):
    """获取特定用户设置"""
    user_id = str(current_user["user_id"])
    value = db_manager.get_user_setting(user_id, setting_key)
    return {"setting_key": setting_key, "setting_value": value}

@app.post("/api/characters/{character_id}/skills/{skill_name}")
async def use_character_skill(character_id: str, skill_name: str, params: Dict[str, Any], current_user: dict = Depends(get_current_user)):
    """使用角色技能"""
    character = character_manager.get_character(character_id)
    if not character:
        raise HTTPException(status_code=404, detail="角色不存在")
    
    result = await character_manager.use_skill(character_id, skill_name, params)
    
    # 保存技能使用记录
    if "result" in result:
        user_id = str(current_user["user_id"])
        db_manager.save_chat_record(character_id, "assistant", f"【{skill_name}】{result['result']}", "skill", user_id)
    
    return result

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
