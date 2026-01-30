"""
助农食育AI数字小人后端服务
作者：你的大学生创新创业项目
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import requests
import os
import json
from datetime import datetime
from typing import Dict, List, Optional
from dotenv import load_dotenv
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 加载环境变量
load_dotenv()

# 创建FastAPI应用
app = FastAPI(
    title="助农食育AI助手API",
    description="大学生创新创业项目 - AI数字小人后端服务",
    version="1.0.0"
)

# 配置CORS（允许前端访问）
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5500",  # Live Server默认端口
        "http://127.0.0.1:5500",
        "http://localhost:3000",
        "*"  # 开发阶段允许所有，上线后需修改为具体域名
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# 配置DeepSeek API
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"
API_KEY = os.getenv("DEEPSEEK_API_KEY")

# 定义数字小人的系统角色和专业知识
DIGITAL_ASSISTANT_PROMPT = """你是一个专业的助农食育AI数字小人，名为"小农助手"。请遵循以下规则：

1. **身份定位**：你是连接农田与餐桌的数字化桥梁，专注于农产品推广和健康饮食教育
2. **专业知识**：
   - 农产品知识：品种特点、种植技术、营养价值、储存方法
   - 饮食健康：营养搭配、节气食疗、食材烹饪建议
   - 助农信息：农产品产销对接、农户故事、乡村特色
3. **对话风格**：
   - 热情友好，富有同理心
   - 用通俗易懂的语言解释专业概念
   - 适当使用emoji增加亲和力
   - 回答要具体实用，避免空洞理论
4. **格式要求**：
   - 重要信息可以分点说明
   - 关键数据用**粗体**强调
   - 每段话不要太长，保持可读性

如果用户的问题超出你的知识范围，请礼貌说明并引导到相关话题。"""

@app.get("/")
async def root():
    """健康检查端点"""
    return {
        "status": "running",
        "service": "助农食育AI数字小人",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/status")
async def get_status():
    """获取服务状态"""
    return {
        "assistant_name": "小农助手",
        "description": "助农食育AI数字小人",
        "api_status": "active" if API_KEY else "inactive",
        "model": "deepseek-chat",
        "max_tokens": 2000
    }

@app.post("/api/chat")
async def chat_with_assistant(request: Dict):
    """
    与AI数字小人对话
    请求格式: {"message": "你的问题", "conversation_id": "可选会话ID"}
    """
    if not API_KEY:
        logger.error("API Key未配置")
        raise HTTPException(status_code=500, detail="API Key未配置，请检查环境变量")
    
    user_message = request.get("message", "").strip()
    conversation_id = request.get("conversation_id", "")
    
    if not user_message:
        raise HTTPException(status_code=400, detail="消息内容不能为空")
    
    logger.info(f"收到用户消息: {user_message[:50]}...")
    
    try:
        # 构建对话历史（简单实现，实际可集成数据库）
        messages = [
            {"role": "system", "content": DIGITAL_ASSISTANT_PROMPT},
            {"role": "user", "content": user_message}
        ]
        
        # 准备请求数据
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "deepseek-chat",
            "messages": messages,
            "temperature": 0.7,  # 控制创造性
            "max_tokens": 1000,  # 回复最大长度
            "stream": False
        }
        
        # 调用DeepSeek API
        logger.info("正在调用DeepSeek API...")
        response = requests.post(
            DEEPSEEK_API_URL,
            headers=headers,
            json=data,
            timeout=30  # 30秒超时
        )
        
        # 检查响应
        response.raise_for_status()
        result = response.json()
        
        # 提取AI回复
        ai_reply = result["choices"][0]["message"]["content"]
        
        # 记录token使用情况（用于监控成本）
        usage = result.get("usage", {})
        logger.info(f"API调用完成，使用token: {usage.get('total_tokens', 0)}")
        
        # 构建响应
        response_data = {
            "reply": ai_reply,
            "assistant": "小农助手",
            "conversation_id": conversation_id or f"conv_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "timestamp": datetime.now().isoformat(),
            "usage": {
                "tokens_used": usage.get("total_tokens", 0),
                "prompt_tokens": usage.get("prompt_tokens", 0),
                "completion_tokens": usage.get("completion_tokens", 0)
            }
        }
        
        return JSONResponse(content=response_data)
        
    except requests.exceptions.Timeout:
        logger.error("API请求超时")
        raise HTTPException(status_code=504, detail="请求超时，请稍后重试")
    except requests.exceptions.RequestException as e:
        logger.error(f"API请求失败: {str(e)}")
        raise HTTPException(status_code=502, detail=f"AI服务暂时不可用: {str(e)}")
    except KeyError as e:
        logger.error(f"解析API响应失败: {str(e)}")
        raise HTTPException(status_code=500, detail="AI服务响应格式错误")
    except Exception as e:
        logger.error(f"未知错误: {str(e)}")
        raise HTTPException(status_code=500, detail=f"系统错误: {str(e)}")

@app.get("/api/examples")
async def get_example_questions():
    """获取示例问题，用于前端引导"""
    examples = [
        "这个季节有什么当季的农产品推荐？",
        "如何保存刚买的新鲜蔬菜？",
        "番茄有什么营养价值？",
        "请给我一个简单的农家菜食谱",
        "有机农业和传统农业有什么区别？",
        "如何辨别新鲜的土鸡蛋？",
        "糖尿病患者适合吃什么水果？",
        "讲讲农民种植水稻的故事",
        "怎样减少食物浪费？",
        "本地特色农产品有哪些？"
    ]
    return {"examples": examples}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        app,
        host="0.0.0.0",  # 允许所有网络访问
        port=port,
        reload=True  # 开发模式，代码更改自动重启
    )
  