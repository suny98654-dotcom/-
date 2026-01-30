import requests
import json

def test_chat_api():
    """测试聊天API"""
    url = "http://127.0.0.1:8000/api/chat"
    
    test_message = {
        "message": "你好，请介绍一下你自己",
        "conversation_id": "test_001"
    }
    
    try:
        response = requests.post(url, json=test_message)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"AI助手: {result['reply'][:100]}...")
            print(f"会话ID: {result['conversation_id']}")
            print(f"Token使用: {result['usage']['tokens_used']}")
        else:
            print(f"错误: {response.text}")
    except Exception as e:
        print(f"请求失败: {e}")

def test_status_api():
    """测试状态API"""
    try:
        response = requests.get("http://127.0.0.1:8000/api/status")
        print(f"服务状态: {response.json()}")
    except Exception as e:
        print(f"状态检查失败: {e}")

if __name__ == "__main__":
    print("=== 测试助农食育AI助手API ===\n")
    
    print("1. 测试服务状态...")
    test_status_api()
    
    print("\n2. 测试聊天功能...")
    test_chat_api()