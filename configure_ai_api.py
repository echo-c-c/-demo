#!/usr/bin/env python3
"""
配置AI对话API密钥
"""

import os

def configure_ai_api():
    """配置AI对话API"""
    print("🤖 配置AI对话API")
    print("=" * 50)
    
    print("当前状态：")
    print(f"✅ 语音识别：七牛云语音服务（已配置）")
    print(f"❌ AI对话：需要配置ALIBABA_CLOUD_API_KEY")
    print()
    
    print("要获得真实的AI角色对话，您需要：")
    print("1. 访问阿里云百炼平台：https://bailian.console.aliyun.com/")
    print("2. 开通Qwen-Max模型服务")
    print("3. 获取API密钥")
    print("4. 设置环境变量")
    print()
    
    # 检查当前环境变量
    current_key = os.getenv("ALIBABA_CLOUD_API_KEY", "")
    if current_key:
        print(f"当前API密钥：{current_key[:10]}...")
    else:
        print("当前API密钥：未配置")
    
    print()
    print("配置方法：")
    print("方法1 - 临时设置（当前会话）：")
    print('$env:ALIBABA_CLOUD_API_KEY="your_api_key_here"')
    print()
    print("方法2 - 永久设置（系统环境变量）：")
    print("在系统环境变量中添加 ALIBABA_CLOUD_API_KEY")
    print()
    print("方法3 - 修改test_start.py：")
    print("在test_start.py中设置真实的API密钥")
    
    print()
    print("配置完成后，重启服务器即可享受真实的AI对话！")

if __name__ == "__main__":
    configure_ai_api()

