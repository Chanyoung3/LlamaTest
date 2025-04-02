import requests
import json

OLLAMA_API_URL = "http://localhost:11434/api/generate"

def ask_llama(prompt):
    payload = {
        "model": "llama3.1:latest",
        "prompt": f"다음 대화를 분석해서 고객과 상담원을 구분해 JSON 형식으로 출력해줘.\n\n{prompt}\n\n형식:\n{{\"dialogue\": [{{\"speaker\": \"고객\", \"text\": \"문장\"}}, {{\"speaker\": \"상담원\", \"text\": \"문장\"}}]}}",
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

with open("conversation.txt", "r", encoding="utf-8") as file:
    conversation = file.read().strip()

result = ask_llama(conversation)
print(json.dumps(result, indent=4, ensure_ascii=False))
