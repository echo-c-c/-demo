#!/usr/bin/env python3
"""
环境变量加载器
确保在启动服务器前正确加载环境变量
"""

import os
from pathlib import Path

def load_environment_variables(env_file: str = "test_env.env") -> None:
    """加载环境变量文件"""
    env_path = Path(env_file)
    if env_path.exists():
        print(f"📁 加载环境变量文件: {env_file}")
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value
        print("✅ 环境变量已加载")
        
        # 显示关键配置
        print("🔧 当前配置:")
        print(f"  - ALIBABA_CLOUD_API_KEY: {'已配置' if os.getenv('ALIBABA_CLOUD_API_KEY') else '未配置'}")
        print(f"  - QINIU_TTS_KEY: {'已配置' if os.getenv('QINIU_TTS_KEY') else '未配置'}")
    else:
        print(f"⚠️  环境变量文件不存在: {env_file}")
        print("💡 请确保 test_env.env 文件存在并包含正确的API密钥")

if __name__ == "__main__":
    load_environment_variables()
