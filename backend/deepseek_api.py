import requests
from config import DEEPSEEK_API_KEY, DEEPSEEK_API_URL

# =========================
# 对话历史容器（全局）
# =========================
chat_history = [
    {
        "role": "system",
        "content": (
            "你是一个友好、自然、有亲和力的助农食育AI助手，"
            "擅长用通俗易懂的语言讲解饮食健康、营养搭配和食品安全。"
            "即使用户只是打招呼，也要正常、热情地回应。"
        )
    }
]

MAX_HISTORY = 8  # 只保留最近 8 条（不含 system）


def chat_with_deepseek(user_message: str) -> str:
    global chat_history

    # 1️⃣ 把用户输入加入历史
    chat_history.append({
        "role": "user",
        "content": user_message
    })

    # 2️⃣ 裁剪历史，防止越聊越慢
    system_msg = chat_history[0]
    other_msgs = chat_history[1:]

    if len(other_msgs) > MAX_HISTORY:
        other_msgs = other_msgs[-MAX_HISTORY:]

    chat_history = [system_msg] + other_msgs

    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "deepseek-chat",
        "messages": chat_history,   # ✅ 关键：用历史，而不是写死
        "temperature": 0.7
    }

    try:
        res = requests.post(
            DEEPSEEK_API_URL,
            headers=headers,
            json=payload,
            timeout=30,
            proxies={
                "http": None,
                "https": None
            }
        )

        res.raise_for_status()
        data = res.json()

        # 3️⃣ 防御式取值
        if "choices" not in data or not data["choices"]:
            reply = "我有点没听清，但我们可以慢慢来 😊 你想聊点什么？"
        else:
            reply = data["choices"][0]["message"]["content"]

        # 4️⃣ 把 AI 回复也存进历史
        chat_history.append({
            "role": "assistant",
            "content": reply
        })

        return reply

    except requests.exceptions.RequestException as e:
        print("DeepSeek Request Error:", e)
        return "网络有点小波动，我们再试一次吧～"

    except Exception as e:
        print("DeepSeek Unknown Error:", e)
        return "我刚刚有点卡住了，但已经恢复啦～你可以继续说 😊"
