# backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from models import ChatRequest, ChatResponse
from deepseek_api import chat_with_deepseek

app = FastAPI(title="食育 AI 后端")

# 允许前端跨域访问（非常重要）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 本地开发先这样
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    reply = chat_with_deepseek(req.message)
    return {"reply": reply}
