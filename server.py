from flask import Flask, request, jsonify
import requests
import json
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # CORS 설정 (프론트엔드에서 요청 허용)

OLLAMA_API_URL = "http://localhost:11434/api/generate"

def ask_llama(conversation):
    payload = {
        "model": "llama3.1:latest",
        "prompt": f"""
다음 상담 데이터를 분석하고 정확한 JSON 형식으로 출력해줘.

상담 데이터:
{conversation}

출력 예시:
```json
{{
    "dialogue": [
        {{"speaker": "고객", "text": "안녕하세요"}},
        {{"speaker": "상담원", "text": "무엇을 도와드릴까요?"}}
    ]
}}""",
"stream": False
    }
    
    response = requests.post(OLLAMA_API_URL, json=payload)

    if response.status_code == 200:
        response_text = response.json().get("response", "").strip()
        
        try:
            parsed_json = json.loads(response_text)
            return parsed_json
        except json.JSONDecodeError:
            return {"error": "Invalid JSON format", "raw_response": response_text}
    else:
        return {"error": response.status_code, "message": response.text}

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get("message", "")

    if not user_message:
        return jsonify({"reply": "메시지를 입력하세요."})

    # LLAMA 모델 호출
    output = ask_llama(user_message)

    return jsonify({"reply": output})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
