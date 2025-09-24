```

```

# ⏰ 时光对话者 - TimeTalker

一个基于AI的角色扮演聊天网站，用户可以与历史人物、文学角色进行深度对话，体验不同的人生智慧。穿越时空，与伟大的灵魂对话！

## 功能特点

### 🎭 丰富的角色库

- **哈利波特** - 魔法世界的年轻巫师，勇敢善良
- **苏格拉底** - 古希腊哲学家，以苏格拉底式问答法闻名
- **爱因斯坦** - 伟大的物理学家，相对论的创立者
- **莎士比亚** - 英国文学巨匠，戏剧大师
- **达芬奇** - 文艺复兴时期的全才，画家、发明家、科学家

### 🔐 用户认证系统

- **用户注册登录** - 安全的用户账户管理
- **JWT令牌认证** - 安全的身份验证机制
- **个人资料管理** - 用户信息维护和更新

### 🗣️ 多种交互方式

- **文本聊天** - 实时文本对话
- **语音聊天** - 语音识别和TTS语音合成
- **WebSocket实时通信** - 低延迟的实时对话体验

### 🎯 角色专属技能

每个角色都具备独特的技能：

#### 哈利波特

- 魔法知识 - 解答魔法相关问题
- 故事创作 - 创作魔法世界的故事
- 人生建议 - 基于勇气和友谊的建议
- 问答解惑 - 魔法史和咒语知识

#### 苏格拉底

- 哲学思辨 - 深度哲学讨论
- 智慧建议 - 基于哲学智慧的人生指导
- 深度问答 - 苏格拉底式问答法
- 逻辑推理 - 帮助理清思维逻辑

#### 爱因斯坦

- 科学解释 - 物理学和科学知识
- 创新思维 - 科学创新和问题解决
- 教育指导 - 科学学习方法
- 哲学思考 - 科学哲学思考

#### 莎士比亚

- 文学创作 - 诗歌和戏剧创作
- 情感分析 - 人性情感分析
- 语言艺术 - 优美的语言表达
- 人生感悟 - 基于文学的人生智慧

#### 达芬奇

- 艺术指导 - 绘画和艺术创作
- 科学解释 - 多领域科学知识
- 创新设计 - 工程和发明设计
- 观察分析 - 敏锐的观察和分析

## 技术架构

### 后端技术栈

- **FastAPI** - 现代、快速的Python Web框架
- **SQLite** - 轻量级数据库
- **WebSocket** - 实时双向通信
- **阿里云百炼平台** - AI大模型服务
- **通义千问3-Max-Preview** - 强大的中文大语言模型

### 前端技术栈

- **Vue 3** - 渐进式JavaScript框架
- **Axios** - HTTP客户端
- **WebSocket API** - 实时通信
- **响应式设计** - 适配各种设备

### 核心服务

- **AI服务** - 集成阿里云百炼平台，实现角色对话
- **语音服务** - 语音识别和TTS语音合成
- **角色管理** - 角色数据管理和技能调用
- **数据库管理** - 聊天记录和用户数据存储

## 安装和运行

### 环境要求

- Python 3.10+
- Windows 10/11（或其他能运行 Python 的系统）

### 安装步骤（已在仓库中提供自动启动脚本）

1. 克隆项目

```bash
git clone https://github.com/echo-c-c/-demo.git
cd -demo
```

2. 安装依赖

```bash
pip install -r requirements.txt
```

3. 配置环境变量（不要把真实密钥写进仓库）

- 创建 `.env` 文件，并按需填写：

```
# 阿里云百炼平台API密钥 (必需)
ALIBABA_CLOUD_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# 七牛云语音服务配置 (可选，用于语音功能)
QINIU_BASE_URL=https://openai.qiniu.com/v1
QINIU_TTS_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# JWT密钥 (用于用户认证，请修改为随机字符串)
JWT_SECRET=your-secret-key-here-please-change-me

# 数据库配置
DATABASE_URL=sqlite:///./chat_database.db

# 调试模式
DEBUG=True
```

4. 启动服务

```bash
python run.py
```

5. 访问应用：
   打开浏览器 `http://localhost:8000`

## API接口

### 角色相关

- `GET /api/characters` - 获取所有角色
- `GET /api/characters/search?query={query}` - 搜索角色
- `GET /api/characters/{character_id}` - 获取特定角色信息

### 聊天相关

- `POST /api/chat/text` - 文本聊天
- `POST /api/chat/voice` - 语音聊天
- `WebSocket /ws/{character_id}` - 实时聊天
- `GET /api/chat/history/{character_id}` - 获取聊天历史

### 技能相关

- `POST /api/characters/{character_id}/skills/{skill_name}` - 使用角色技能

## 使用说明

### 基本使用

1. 在左侧角色列表中选择感兴趣的角色
2. 在聊天框中输入消息开始对话
3. 使用角色专属技能获得更专业的回答

### 技能使用

1. 点击角色技能按钮
2. 根据提示输入相关参数
3. 获得基于角色背景的专业回答

### 语音功能（ASR + TTS + WebSocket通话）

1. 选择角色后，点击右下角的麦克风悬浮按钮开始录音
2. 停止录音后，前端会将音频通过 WebSocket 发送至后端，后端完成 ASR → LLM → TTS 流程
3. 前端自动播放 AI 语音回复，同时在消息区显示识别文本与回复文本

## 项目结构

```
ai-roleplay-chat/
├── backend/
│   ├── main.py              # FastAPI主应用
│   ├── ai_service.py        # AI服务集成
│   ├── voice_service.py     # 语音服务
│   ├── database.py          # 数据库管理
│   ├── character_manager.py # 角色管理
│   ├── auth_service.py      # 认证服务
│   └── chat_database.db     # SQLite数据库
├── frontend/
│   ├── index.html           # Vue前端页面
│   └── images/
│       └── characters/      # 角色图片资源
│           ├── harry_potter.jpg
│           ├── socrates.jpg
│           ├── einstein.jpg
│           ├── shakespeare.jpg
│           └── leonardo_da_vinci.jpg
├── requirements.txt         # Python依赖
├── run.py                   # 启动脚本
├── .env                     # 环境变量配置
└── README.md               # 项目说明
```

## 开发计划

### 已完成功能

- ✅ 基础角色系统、角色技能（含"魔法知识"等）
- ✅ 阿里云百炼（通义千问3）对话集成
- ✅ 用户注册/登录、JWT 鉴权
- ✅ 聊天记录、收藏、用户设置、通知面板
- ✅ 主题切换（亮/暗/自动）、整体UI重构
- ✅ 语音识别（ASR）与语音合成（TTS）整合、语音通话
- ✅ 角色图片资源集成（高质量角色头像）
- ✅ 前端认证问题修复（401错误处理）
- ✅ 环境变量配置优化
- ✅ 静态文件服务配置

### 最新更新 (v1.1.0)

- 🆕 集成高质量角色图片资源
- 🆕 优化前端认证流程
- 🆕 改进错误处理和用户体验
- 🆕 完善环境变量配置
- 🆕 静态文件服务优化

### 规划项

- 🔄 更丰富的角色与技能
- 🔄 更完善的消息搜索与导出
- 🔄 评分与反馈体系
- 🔄 多语言支持
- 🔄 移动端适配优化

## 故障排除

### 常见问题

1. **API调用401错误**
   - 确保已正确配置 `ALIBABA_CLOUD_API_KEY`
   - 检查 `.env` 文件是否存在且格式正确
   - 重启服务器以加载新的环境变量

2. **角色图片无法显示**
   - 确保图片文件存在于 `frontend/images/characters/` 目录
   - 检查静态文件服务配置是否正确

3. **语音功能无法使用**
   - 确保已配置 `QINIU_TTS_KEY`
   - 检查浏览器是否支持WebRTC
   - 确保在HTTPS环境下使用（语音功能需要安全上下文）

4. **用户认证问题**
   - 清除浏览器本地存储
   - 检查JWT密钥配置
   - 确保数据库文件权限正确

### 获取帮助

如果遇到其他问题，请：
1. 查看浏览器控制台错误信息
2. 检查服务器日志输出
3. 提交Issue到GitHub仓库

## 贡献指南

欢迎提交Issue和Pull Request来改进这个项目！

## 许可证

MIT License

## 联系方式

如有问题或建议，请通过以下方式联系：

- 邮箱：2012997697@qq.com
- GitHub：echo-c-c
