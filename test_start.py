#!/usr/bin/env python3
"""
测试模式启动脚本 - 无需API密钥即可运行
"""

import os
import sys
import subprocess
import webbrowser
import time
from pathlib import Path

def setup_test_environment():
    """设置测试环境"""
    print("🧪 设置测试环境...")
    
    # 设置测试环境变量
    os.environ["ALIBABA_CLOUD_API_KEY"] = ""
    os.environ["QINIU_TTS_KEY"] = ""
    os.environ["SECRET_KEY"] = "test-secret-key-for-demo"
    os.environ["DEBUG"] = "True"
    os.environ["TEST_MODE"] = "True"
    
    print("✅ 测试环境变量已设置")
    print("   - 语音功能将使用模拟数据")
    print("   - AI对话功能需要配置ALIBABA_CLOUD_API_KEY才能正常工作")

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

def find_available_port(start_port=8080, max_port=8090):
    """查找可用端口"""
    import socket
    for port in range(start_port, max_port + 1):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            result = sock.connect_ex(('localhost', port))
            if result != 0:
                print(f"✅ 找到可用端口: {port}")
                return port
        finally:
            sock.close()
    
    print(f"❌ 在端口 {start_port}-{max_port} 范围内未找到可用端口")
    return None

def start_test_server(port=8080):
    """启动测试服务器"""
    print("🚀 启动测试模式服务器...")
    print(f"📍 服务器地址: http://localhost:{port}")
    print("🧪 测试模式特性:")
    print("   - 语音识别返回模拟结果")
    print("   - 语音合成生成模拟音频")
    print("   - 无需API密钥即可运行")
    print("⏹️  按 Ctrl+C 停止服务器")
    print("-" * 50)
    
    # 切换到backend目录
    backend_dir = Path("backend")
    if backend_dir.exists():
        os.chdir(backend_dir)
    
    try:
        # 启动FastAPI服务器
        print(f"🔄 启动在端口 {port}...")
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "main:app", 
            "--host", "127.0.0.1", 
            "--port", str(port), 
            "--reload"
        ])
    except KeyboardInterrupt:
        print("\n👋 测试服务器已停止")
    except Exception as e:
        print(f"❌ 端口 {port} 启动失败: {e}")
        sys.exit(1)

def open_browser(port=8080):
    """打开浏览器"""
    def open_after_delay():
        time.sleep(3)  # 等待服务器启动
        try:
            webbrowser.open(f"http://localhost:{port}")
            print("🌐 浏览器已打开")
        except Exception as e:
            print(f"⚠️  无法自动打开浏览器: {e}")
            print(f"请手动访问: http://localhost:{port}")
    
    import threading
    threading.Thread(target=open_after_delay, daemon=True).start()

def main():
    """主函数"""
    print("🧪 AI角色扮演聊天系统 - 测试模式")
    print("=" * 50)
    
    # 设置测试环境
    setup_test_environment()
    
    # 检查Python版本
    check_python_version()
    
    # 安装依赖
    install_requirements()
    
    # 查找可用端口
    port = find_available_port()
    if port is None:
        print("❌ 无法找到可用端口")
        sys.exit(1)
    
    print(f"🎯 使用端口: {port}")
    
    # 打开浏览器
    open_browser(port)
    
    # 启动服务器
    start_test_server(port)

if __name__ == "__main__":
    main()
