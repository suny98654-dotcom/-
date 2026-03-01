# backend/config.py
import os

# 从系统环境变量读取
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

if not DEEPSEEK_API_KEY:
    raise ValueError("未设置 DEEPSEEK_API_KEY 环境变量")

DEEPSEEK_API_URL = "https://api.deepseek.com/chat/completions"
