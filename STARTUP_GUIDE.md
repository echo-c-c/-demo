# 项目启动指南

## 🚀 快速启动（推荐）

### 方法1：使用启动脚本（最简单）
```bash
python run.py
```

### 方法2：手动启动服务器
```bash
# 进入backend目录
cd backend

# 启动服务器
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

## 🔧 详细启动步骤

### 1. 检查环境
```bash
# 检查Python版本（需要3.8+）
python --version

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置环境变量
确保 `test_env.env` 文件存在并包含正确的API密钥：
```bash
# 检查环境变量文件
type test_env.env
```

### 3. 启动服务器
```bash
# 方法A：使用启动脚本（推荐）
python run.py

# 方法B：手动启动
cd backend
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload

# 方法C：使用生产启动脚本
python start_server.py --host 127.0.0.1 --port 8000
```

## 🌐 访问应用

启动成功后，访问：
- **前端界面**：http://localhost:8000
- **API文档**：http://localhost:8000/docs
- **健康检查**：http://localhost:8000/health

## 🛠️ 故障排除

### 问题1：找不到main模块
```
ERROR: Error loading ASGI app. Could not import module "main".
```
**解决方案**：确保在 `backend` 目录中运行命令
```bash
cd backend
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

### 问题2：端口被占用
```
ERROR: [Errno 10048] Only one usage of each socket address
```
**解决方案**：使用其他端口或终止占用端口的进程
```bash
# 使用其他端口
python -m uvicorn main:app --host 127.0.0.1 --port 8001 --reload

# 或终止占用端口的进程
netstat -ano | findstr :8000
taskkill /PID <进程ID> /F
```

### 问题3：依赖包缺失
```
ModuleNotFoundError: No module named 'xxx'
```
**解决方案**：安装依赖包
```bash
pip install -r requirements.txt
```

### 问题4：环境变量未加载
```
TTS API错误: access denied for invalid api key
```
**解决方案**：检查环境变量文件
```bash
# 运行诊断工具
python fix_tts_api.py
```

## 📋 启动检查清单

- [ ] Python 3.8+ 已安装
- [ ] 依赖包已安装 (`pip install -r requirements.txt`)
- [ ] 环境变量文件存在 (`test_env.env`)
- [ ] 在正确的目录中运行命令
- [ ] 端口8000可用
- [ ] 防火墙允许访问

## 🎯 推荐启动流程

1. **打开命令提示符**
2. **进入项目目录**
   ```bash
   cd "E:\桌面\七牛云校招(1)"
   ```
3. **运行启动脚本**
   ```bash
   python run.py
   ```
4. **等待服务器启动**
5. **打开浏览器访问** http://localhost:8000

## 🔍 验证启动成功

看到以下信息表示启动成功：
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [xxxx] using StatReload
INFO:     Started server process [xxxx]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```
