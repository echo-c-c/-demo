# 测试模式说明

## 概述

已为TTS和ASR功能添加测试模式支持，无需API密钥即可运行和测试语音功能。

## 修改内容

### 1. 后端语音服务 (`backend/voice_service.py`)

**ASR功能 (语音转文字)**
- ✅ 无API密钥时返回模拟识别结果
- ✅ API错误时返回模拟结果而不是错误信息
- ✅ 异常时返回模拟结果

**TTS功能 (文字转语音)**
- ✅ 无API密钥时返回模拟音频数据（静音MP3）
- ✅ API错误时返回模拟音频而不是抛出异常
- ✅ 异常时返回模拟音频

**音色获取**
- ✅ 无API密钥时使用默认音色
- ✅ 异常时使用默认音色

### 2. 独立测试脚本

**ASR测试 (`asr.py`)**
- ✅ 无API密钥时显示模拟识别结果
- ✅ 不会因缺少密钥而崩溃

**TTS测试 (`tts.py`)**
- ✅ 无API密钥时生成模拟音频文件
- ✅ 不会因缺少密钥而崩溃

### 3. 测试启动脚本 (`test_start.py`)

- ✅ 自动设置测试环境变量
- ✅ 无需API密钥即可启动服务器
- ✅ 自动查找可用端口
- ✅ 自动打开浏览器

## 使用方法

### 方法1：使用测试启动脚本（推荐）

```bash
python test_start.py
```

### 方法2：手动设置环境变量

```bash
# Windows PowerShell
$env:ALIBABA_CLOUD_API_KEY=""
$env:QINIU_TTS_KEY=""
python start_server.py

# Linux/Mac
export ALIBABA_CLOUD_API_KEY=""
export QINIU_TTS_KEY=""
python start_server.py
```

### 方法3：使用测试环境文件

```bash
# 复制测试环境文件
copy test_env.env .env

# 启动服务器
python start_server.py
```

## 测试模式特性

### 语音识别 (ASR)
- 返回固定文本："这是测试模式的语音识别结果"
- 不会因API错误而中断服务
- 日志显示"测试模式"标识

### 语音合成 (TTS)
- 生成静音MP3音频文件
- 不会因API错误而中断服务
- 日志显示"测试模式"标识

### 音色选择
- 使用默认音色："zh-CN-XiaoxiaoNeural"
- 不会因API错误而中断服务

## 测试验证

### 1. 测试ASR独立脚本
```bash
python asr.py
# 输出：测试模式：ASR配置缺失，使用模拟识别结果
```

### 2. 测试TTS独立脚本
```bash
python tts.py
# 输出：测试模式：TTS配置缺失，使用模拟音频生成
# 生成：tts_out.mp3（静音音频文件）
```

### 3. 测试完整服务器
```bash
python test_start.py
# 启动服务器，访问 http://localhost:8080
# 语音功能将使用模拟数据
```

## 生产环境切换

要切换到生产环境，只需设置真实的API密钥：

```bash
# 设置真实API密钥
export ALIBABA_CLOUD_API_KEY="sk-your-real-key"
export QINIU_TTS_KEY="sk-your-real-key"

# 启动服务器
python start_server.py
```

## 注意事项

1. **AI对话功能**：仍需要配置 `ALIBABA_CLOUD_API_KEY` 才能正常工作
2. **模拟音频**：TTS生成的模拟音频是静音文件，仅用于测试流程
3. **模拟文本**：ASR返回的模拟文本是固定内容，仅用于测试流程
4. **日志标识**：所有测试模式操作都会在日志中显示"测试模式"标识

## 文件清单

- `backend/voice_service.py` - 后端语音服务（已修改）
- `asr.py` - ASR独立测试脚本（已修改）
- `tts.py` - TTS独立测试脚本（已修改）
- `test_start.py` - 测试模式启动脚本（新增）
- `test_env.env` - 测试环境变量文件（新增）
- `TEST_MODE_README.md` - 本说明文档（新增）
