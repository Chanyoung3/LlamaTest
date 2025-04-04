import requests
import json

OLLAMA_API_URL = "http://localhost:11434/api/generate"

def ask_llama(conversation):
    payload = {
        "model": "llama3.1:latest",
        "prompt": f"다음 상담 데이터를 분석하고 정확한 JSON 형식으로 출력해줘.\n\n{conversation}\n\n출력 예시:\n{{\"dialogue\": [{{\"speaker\": \"고객\", \"text\": \"안녕하세요\"}}, {{\"speaker\": \"상담원\", \"text\": \"무엇을 도와드릴까요?\"}}]}}",
        "stream": False
    }
    
    response = requests.post(OLLAMA_API_URL, json=payload)

    if response.status_code == 200:
        response_text = response.json().get("response", "").strip()
        print("LLAMA 응답:", response_text)
        
        try:
            parsed_json = json.loads(response_text)
            return parsed_json
        except json.JSONDecodeError:
            return {"error": "Invalid JSON format", "raw_response": response_text}
    else:
        return {"error": response.status_code, "message": response.text}


def check_llama(conversation):
    payload = {
        "model": "llama3.1:latest",
        "prompt": f"스크립트에 있는 내용을 잘 준수했는지 솔루션을 포함해서 출력해줘:\n\n{conversation}",
        "stream": False
    }
    
    response = requests.post(OLLAMA_API_URL, json=payload)

    if response.status_code == 200:
        response_text = response.json().get("response", "").strip()
        print("LLAMA 응답:", response_text)
        
        try:
            parsed_json = json.loads(response_text)
            return parsed_json
        except json.JSONDecodeError:
            return {"error": "Invalid JSON format", "raw_response": response_text}
    else:
        return {"error": response.status_code, "message": response.text}

# 상담 데이터 파일 읽기
with open("conversation.txt", "r", encoding="utf-8") as file:
    conversation_data = file.read().strip()

# LLAMA 호출 및 결과 저장
result = ask_llama(conversation_data)
result2 = check_llama(conversation_data)

# JSON 파일로 저장
with open("result.json", "w", encoding="utf-8") as outfile:
    json.dump(result, outfile, indent=4, ensure_ascii=False)

print("✅ 분석 결과가 result.json 파일로 저장되었습니다.")
print(json.dumps(result2, indent=4, ensure_ascii=False))