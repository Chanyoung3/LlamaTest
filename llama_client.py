# llama_client.py
import requests
import json

OLLAMA_API_URL = "http://localhost:11434/api/generate"

def ask_llama(conversation):
    payload = {
        "model": "llama3.1:latest",
        "prompt": (
            "다음 상담 데이터를 분석하고 정확한 JSON 형식으로 출력해줘.\n\n"
            f"{conversation}\n\n"
            "출력 예시:\n"
            "{\"dialogue\": [{\"speaker\": \"고객\", \"text\": \"안녕하세요\"}, {\"speaker\": \"상담원\", \"text\": \"무엇을 도와드릴까요?\"}]}"
        ),
        "stream": False
    }

    try:
        response = requests.post(OLLAMA_API_URL, json=payload)
        if response.status_code == 200:
            response_text = response.json().get("response", "").strip()
            return json.loads(response_text)
        else:
            return {"error": f"HTTP {response.status_code}", "message": response.text}
    except requests.exceptions.RequestException as e:
        return {"error": "Request failed", "message": str(e)}
    except json.JSONDecodeError:
        return {"error": "Invalid JSON response", "raw": response_text}
