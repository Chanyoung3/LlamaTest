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

@app.route('/upload-script', methods=['POST'])
def upload_script():
    global script_prompt

    file = request.files.get('script')
    if not file:
        return jsonify({"error": "No file uploaded"}), 400

    # 엑셀 읽기
    try:
        df = pd.read_excel(file)
        script_text = "\n".join(df.astype(str).apply(lambda row: " ".join(row), axis=1).tolist())
        script_prompt = f"앞으로 이 기준 스크립트를 참고하여 응답해 주세요:\n\n{script_text}"
        return jsonify({"message": "스크립트 저장 완료", "script_summary": script_text[:200]})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/data-script', methods=['POST'])
def data_script():
    from llama_client import ask_llama
    import re
    import json
    import io
    import uuid
    from flask import send_file

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

        prompt = f"""
        다음은 여러 건의 고객 상담 대화 내용입니다. 전체 내용을 종합하여 다음 네 가지 항목에 대해 한줄로 정리해 제시해 주세요:
        1. 고객의 전반적인 감정 경향
        2. 주요 상담 유형
        3. 자주 발생하는 규정 위반 사례
        4. 상담의 전반적인 흐름이나 단계 구성
        
        상담 내용:
        \"\"\"{full_dialogue}\"\"\"
        
        결과는 보기 좋게 JSON 형식으로 요약해 주세요.
        """
        llama_response = ask_llama(prompt, mode="analyze")

        if isinstance(llama_response, dict):
            llama_text = json.dumps(llama_response, ensure_ascii=False, indent=2)
        else:
            llama_text = str(llama_response)

        json_match = re.search(r"```json\n(.*?)\n```", llama_text, re.DOTALL)
        formatted_text = ""
        if json_match:
            try:
                parsed_json = json.loads(json_match.group(1))
                for key, value in parsed_json.items():
                    formatted_text += f"📌 {key}\n{json.dumps(value, ensure_ascii=False, indent=2)}\n\n"
            except json.JSONDecodeError:
                formatted_text = llama_text
        else:
            formatted_text = llama_text

        # 텍스트 파일을 임시로 저장 (예: static 폴더)
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
        return jsonify({"error": str(e)}), 500



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