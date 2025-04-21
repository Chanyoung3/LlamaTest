import requests
import json

OLLAMA_API_URL = "http://localhost:11434/api/generate"

def ask_llama(user_input, mode="default"):
    if mode == "analyze":
        prompt = (
        "<|begin_of_text|>\n"
        "<|start_header_id|>system<|end_header_id|>\n"
        "다음 상담 데이터를 분석하여 아래 항목들을 평가해주세요. 응답은 JSON 형식으로 정확히 출력해주세요.\n\n"
        "[기본 체크]\n"
        "- 본인확인: 상담사가 고객의 신원을 확인했는지?\n"
        "- 소속안내: 회사명 또는 조직을 명확히 언급했는지?\n"
        "- 용건안내: 상담 목적을 설명했는지?\n"
        "- 납입안내: 납부 방법/내용을 안내했는지?\n\n"

        "[추가 체크]\n"
        "- 고객이 즉시 납부할 의사가 있는지 판단해줘\n"
        "- 상담사가 욕설 또는 비속어를 사용했는지 여부\n\n"

        "[스크립트 준수 체크]\n"
        "- 소속안내가 본인확인 전에 이루어졌는지? (그럴 경우 스크립트 위반)\n"
        "- 고객이 본인확인에 명확히 응답했는가? ('네', '맞습니다' 등)\n\n"

        "모든 항목은 boolean(true/false)으로 판단하고, 필요한 경우 '이유' 항목도 포함해주세요.\n"
        "<|eom_id|>\n\n"

        "<|start_header_id|>user<|end_header_id|>\n"
        f"{user_input}\n"
        "<|eom_id|>\n\n"

        "<|start_header_id|>assistant<|end_header_id|>\n"
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
