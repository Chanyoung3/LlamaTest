import requests
import json

OLLAMA_API_URL = "http://localhost:11434/api/generate"

def ask_llama(user_input, mode="default"):
    if mode == "analyze":
        prompt = (
            "다음 상담 데이터를 분석하고 정확한 JSON 형식으로 출력해줘.\n\n"
            f"{user_input}\n\n"
            "출력 예시:\n"
            "{\"dialogue\": [{\"speaker\": \"고객\", \"text\": \"안녕하세요\"}, {\"speaker\": \"상담원\", \"text\": \"무엇을 도와드릴까요?\"}]}"
        )
    else:
        prompt = f"콜센터와 관련된 질문이나 대화에 친절히 응답해줘:\n\n{user_input}"

    payload = {
        "model": "llama3.1:latest",
        "prompt": prompt,
        "stream": False
    }

    try:
        response = requests.post(OLLAMA_API_URL, json=payload)
        if response.status_code == 200:
            response_text = response.json().get("response", "").strip()
            try:
                # 분석 모드일 경우 JSON 파싱 시도
                return json.loads(response_text) if mode == "analyze" else {"response": response_text}
            except json.JSONDecodeError:
                return {"error": "Invalid JSON response", "raw": response_text}
        else:
            return {"error": f"HTTP {response.status_code}", "message": response.text}
    except requests.exceptions.RequestException as e:
        return {"error": "Request failed", "message": str(e)}
