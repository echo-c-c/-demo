#!/usr/bin/env python3
"""
AI角色扮演聊天系统启动脚本
"""

import os
import sys
import subprocess
import webbrowser
import time
from pathlib import Path

def check_python_version():
    """检查Python版本"""
    if sys.version_info < (3, 8):
        print("❌ 错误: 需要Python 3.8或更高版本")
        print(f"当前版本: {sys.version}")
        sys.exit(1)
    print(f"✅ Python版本检查通过: {sys.version.split()[0]}")

def install_requirements():
    """安装依赖包"""
    requirements_file = Path("requirements.txt")
    if not requirements_file.exists():
        print("❌ 错误: 找不到requirements.txt文件")
        sys.exit(1)
    
    print("📦 正在安装依赖包...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ 依赖包安装完成")
    except subprocess.CalledProcessError as e:
        print(f"❌ 依赖包安装失败: {e}")
        sys.exit(1)

def create_env_file():
    """创建环境变量文件"""
    env_file = Path(".env")
    if not env_file.exists():
        print("📝 创建环境变量文件...")
        with open(env_file, "w", encoding="utf-8") as f:
            f.write("# AI角色扮演聊天系统环境变量\n")
            f.write("ALIBABA_CLOUD_API_KEY=sk-2796d36fef1048bd91b63f3c355d06dd\n")
            f.write("DATABASE_URL=sqlite:///./chat_database.db\n")
            f.write("DEBUG=True\n")
        print("✅ 环境变量文件创建完成")

def start_server():
    """启动服务器"""
    print("🚀 启动AI角色扮演聊天系统...")
    print("📍 服务器地址: http://localhost:8000")
    print("⏹️  按 Ctrl+C 停止服务器")
    print("-" * 50)
    
    # 切换到backend目录
    backend_dir = Path("backend")
    if backend_dir.exists():
        os.chdir(backend_dir)
    
    try:
        # 启动FastAPI服务器
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "main:app", 
            "--host", "0.0.0.0", 
            "--port", "8000", 
            "--reload"
        ])
    except KeyboardInterrupt:
        print("\n👋 服务器已停止")
    except Exception as e:
        print(f"❌ 服务器启动失败: {e}")
        sys.exit(1)

def open_browser():
    """打开浏览器"""
    def open_after_delay():
        time.sleep(3)  # 等待服务器启动
        try:
            webbrowser.open("http://localhost:8000")
            print("🌐 浏览器已打开")
        except Exception as e:
            print(f"⚠️  无法自动打开浏览器: {e}")
            print("请手动访问: http://localhost:8000")
    
    import threading
    threading.Thread(target=open_after_delay, daemon=True).start()

def main():
    """主函数"""
    print("🎭 AI角色扮演聊天系统")
    print("=" * 50)
    
    # 检查Python版本
    check_python_version()
    
    # 安装依赖
    install_requirements()
    
    # 创建环境变量文件
    create_env_file()
    
    # 打开浏览器
    open_browser()
    
    # 启动服务器
    start_server()

if __name__ == "__main__":
    main()
