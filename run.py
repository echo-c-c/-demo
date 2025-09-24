#!/usr/bin/env python3
"""
AI角色扮演聊天系统启动脚本
"""

import os
import sys
import subprocess
import webbrowser
import time
import socket
import psutil
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

def kill_process_on_port(port):
    """使用Windows命令终止占用端口的进程"""
    try:
        # 使用netstat查找占用端口的进程
        result = subprocess.run(['netstat', '-ano'], capture_output=True, text=True)
        lines = result.stdout.split('\n')
        
        for line in lines:
            if f':{port}' in line and 'LISTENING' in line:
                parts = line.split()
                if len(parts) >= 5:
                    pid = parts[-1]
                    print(f"🔧 发现占用端口 {port} 的进程 PID: {pid}")
                    
                    # 终止进程
                    try:
                        subprocess.run(['taskkill', '/F', '/PID', pid], 
                                     capture_output=True, text=True)
                        print(f"✅ 已终止进程 PID: {pid}")
                        time.sleep(2)  # 等待端口释放
                        return True
                    except Exception as e:
                        print(f"❌ 无法终止进程 PID {pid}: {e}")
                        return False
        
        print(f"⚠️  未找到占用端口 {port} 的进程")
        return False
    except Exception as e:
        print(f"❌ 查找进程失败: {e}")
        return False

def check_and_release_port(port=8000):
    """检查并释放端口"""
    print(f"🔍 检查端口 {port} 状态...")
    
    # 使用Windows命令检查端口
    try:
        result = subprocess.run(['netstat', '-ano'], capture_output=True, text=True)
        if f':{port}' in result.stdout and 'LISTENING' in result.stdout:
            print(f"⚠️  端口 {port} 被占用，正在尝试释放...")
            if kill_process_on_port(port):
                print(f"✅ 端口 {port} 已释放")
                return True
            else:
                print(f"❌ 无法释放端口 {port}")
                return False
        else:
            print(f"✅ 端口 {port} 可用")
            return True
    except Exception as e:
        print(f"⚠️  端口检查出错: {e}")
        return False

def find_available_port(start_port=8000, max_port=8010):
    """查找可用端口"""
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

def create_env_file():
    """创建环境变量文件"""
    env_file = Path(".env")
    if not env_file.exists():
        print("📝 创建环境变量文件...")
        with open(env_file, "w", encoding="utf-8") as f:
            f.write("# AI角色扮演聊天系统环境变量\n")
            f.write("ALIBABA_CLOUD_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx\n")
            f.write("DATABASE_URL=sqlite:///./chat_database.db\n")
            f.write("DEBUG=True\n")
        print("✅ 环境变量文件创建完成")

def start_server(port=8000):
    """启动服务器"""
    print("🚀 启动AI角色扮演聊天系统...")
    print(f"📍 服务器地址: http://localhost:{port}")
    print("⏹️  按 Ctrl+C 停止服务器")
    print("-" * 50)
    
    # 切换到backend目录
    backend_dir = Path("backend")
    if backend_dir.exists():
        os.chdir(backend_dir)
    
    # 尝试多个端口
    ports_to_try = [port, 8001, 8002, 8003, 8004, 8005]
    
    for try_port in ports_to_try:
        print(f"🔄 尝试启动在端口 {try_port}...")
        try:
            # 启动FastAPI服务器
            subprocess.run([
                sys.executable, "-m", "uvicorn", 
                "main:app", 
                "--host", "0.0.0.0", 
                "--port", str(try_port), 
                "--reload"
            ])
            break  # 如果成功启动，跳出循环
        except KeyboardInterrupt:
            print("\n👋 服务器已停止")
            break
        except Exception as e:
            print(f"❌ 端口 {try_port} 启动失败: {e}")
            if try_port == ports_to_try[-1]:
                print("❌ 所有端口都无法启动，请检查系统权限或防火墙设置")
                sys.exit(1)
            else:
                print(f"🔄 尝试下一个端口...")
                continue

def open_browser(port=8000):
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
    print("🎭 AI角色扮演聊天系统")
    print("=" * 50)
    
    # 检查Python版本
    check_python_version()
    
    # 安装依赖
    install_requirements()
    
    # 创建环境变量文件
    create_env_file()
    
    # 检查端口并确定使用的端口
    port = 8000
    if not check_and_release_port(port):
        port = find_available_port(8001, 8010)
        if port is None:
            print("❌ 无法找到可用端口，请手动关闭占用端口的程序")
            sys.exit(1)
    
    # 打开浏览器
    open_browser(port)
    
    # 启动服务器
    start_server(port)

if __name__ == "__main__":
    main()
