from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import pandas as pd
import os

app = Flask(__name__)
CORS(app)

script_prompt = ""

@app.route('/')
def index():
    return render_template('main.html')

@app.route('/chat', methods=['GET'])
def goresult():
    return render_template('chat.html')

@app.route('/result')
def result():
    return render_template('result.html')

@app.route('/data-script', methods=['POST'])
def data_script():
    from llama_client import ask_llama
    import re
    import json
    import io
    import uuid
    import ast
    import traceback
    import pandas as pd
    from flask import send_file, request, jsonify

    file = request.files.get('data')
    if not file:
        return jsonify({"error": "No file uploaded"}), 400

    try:
        filename = file.filename.lower()

        if filename.endswith(".xlsx") or filename.endswith(".xls"):
            import openpyxl
            df = pd.read_excel(file, engine='openpyxl')
        elif filename.endswith(".csv"):
            df = pd.read_csv(file)
        elif filename.endswith(".txt"):
            lines = file.read().decode("utf-8").splitlines()
            df = pd.DataFrame(lines, columns=["대화"])
        else:
            return jsonify({"error": "지원되지 않는 파일 형식입니다."}), 400

        full_dialogue = "\n".join(df.astype(str).apply(lambda row: " ".join(row), axis=1).tolist())

        prompt = f"""<|begin_of_text|>\n
        <|start_header_id|>system<|end_header_id|>\n
        다음 상담 데이터를 분석하여 아래 항목들을 평가해주세요. 응답은 JSON 형식으로 정확히 출력해주세요.

        [체크 항목]
        - 본인확인: 상담사가 고객의 신원을 확인하는 멘트 (예: '[고객이름]고객님 본인 맞으십니까?')의 여부와 본인확인에 대해 고객이 이에 대한 명확한 답변(예: '네', '맞습니다')을 했는지 여부를 확인해주세요.
        - 소속안내: 회사명 또는 조직을 명확히 언급했는지? (예: '캡스토니 캐피탈의 [상담원이름]입니다.') 만약 본인확인 전에 소속안내를 했다면 불인정.
        - 용건안내: 상담 목적을 명확히 설명했는지? (예: '다름 아니라, ㅇㅇ할부건 00월 00일자 할부금 000000원이 자동이체 통장에서 인출 확인이되지 않아 안내전화드렸습니다.').
        - 납입안내: 납부 방법 또는 납부 내용에 대해 안내했는지?(예: '<자동이체 방식 안내 시> 4시전 입금하시면 당일입금됩니다 OR 유지하면 당일 인출됩니다. <가상계좌 방식 안내 시> 이중출금 될 수 있어 자동이체 통장은 오늘 하루 비워주시고, 오후11시까지 이용 가능합니다.').
        - 납부의사: 고객이 즉시 납부할 의사가 있는지? (예: 고객의 발언에서 납부 의사를 직접 확인).
        - 금지용어: 상담사가 욕설 또는 비속어를 사용했는지? (예: 상담사의 발언에서 부적절한 언어 사용 여부).

        각 항목은 아래 JSON 형식으로 출력하세요:

        반드시 다음과 같은 JSON 형식으로만 응답하세요 (설명 없이):
        {{
        "output": {{
            "본인확인": {{ "결과": true, "이유": "고객이 '네, 맞습니다'라고 응답함" }},
            "소속안내": {{ "결과": false, "이유": "본인확인 전에 소속 안내함" }},
            ...
        }}
        }}

        - 절대 설명문 없이 JSON 만 출력
        - 절대 ```json 등 코드 블럭 사용 금지
        <|eom_id|>

        <|start_header_id|>user<|end_header_id|>\n
        {full_dialogue}
        <|eom_id|>

        <|start_header_id|>assistant<|end_header_id|>\n"""

        llama_response = ask_llama(prompt, mode="analyze")

        # 응답 파싱 및 정제
        try:
            if isinstance(llama_response, dict):
                parsed_json = llama_response.get("output", llama_response)

            elif isinstance(llama_response, str):
                # 코드 블럭 제거
                cleaned_response = re.sub(r"```json\s*\n?(.*?)\n?```", r"\1", llama_response, flags=re.DOTALL).strip()

                try:
                    parsed_all = json.loads(cleaned_response)
                except json.JSONDecodeError:
                    parsed_all = ast.literal_eval(cleaned_response)

                parsed_json = parsed_all.get("output", parsed_all)

            else:
                raise ValueError("Invalid response type from model")

        except Exception as e:
            traceback_str = traceback.format_exc()
            return jsonify({
                "error": f"JSON 파싱 실패: {str(e)}",
                "trace": traceback_str,
                "raw_response": llama_response
            }), 500

        # 결과 포맷팅
        formatted_text = ""
        for key, value in parsed_json.items():
            formatted_text += f"{key}\n{json.dumps(value, ensure_ascii=False, indent=2)}\n\n"

        # 텍스트 파일 저장
        file_id = str(uuid.uuid4())
        file_path = f"static/llama_result_{file_id}.txt"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(formatted_text)

        return jsonify({
            "status": "success",
            "message": "분석 완료",
            "file_url": f"/{file_path}",
            "preview": formatted_text[:300] + "..."
        })

    except Exception as e:
        traceback_str = traceback.format_exc()
        return jsonify({
            "error": str(e),
            "trace": traceback_str
        }), 500



# 예시: 채팅 요청 처리 (LLaMA 연동)
@app.route('/llama-analyze', methods=['POST'])
def analyze():
    from llama_client import ask_llama

    user_message = request.json.get('message', '')
    mode = request.json.get('mode', 'default')
    global script_prompt
    full_prompt = f"{script_prompt}\n\n{user_message}"
    result = ask_llama(full_prompt, mode)
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)