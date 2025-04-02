import requests
import json

# Ollama의 기본 API 주소
OLLAMA_API_URL = "http://localhost:11434/api/generate"

def ask_llama(prompt):
    payload = {
        "model": "llama3.1:latest",
        "prompt": prompt,
        "stream": False
    }
    
    response = requests.post(OLLAMA_API_URL, json=payload)
    
    if response.status_code == 200:
        return response.json()["response"]
    else:
        return f"Error: {response.status_code}, {response.text}"

# 사용자 입력 루프
print("LLama 챗봇입니다. 질문을 입력하세요. ('exit' 입력 시 종료)")
while True:
    user_input = input(">> ")  # 사용자 입력 받기
    if user_input.lower() == "exit":
        print("챗봇을 종료합니다.")
        break
    response = ask_llama(user_input)
    print(response)
