from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import pandas as pd
import os

app = Flask(__name__)
CORS(app)

# 글로벌 변수로 저장
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
        script_prompt = f"이 기준 스크립트를 참고하여 응답해 주세요:\n\n{script_text}"
        return jsonify({"message": "스크립트 저장 완료", "script_summary": script_text[:200]})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 예시: 채팅 요청 처리 (LLaMA 연동)
@app.route('/llama-analyze', methods=['POST'])
def analyze():
    from llama_client import ask_llama

    user_message = request.json.get('message', '')
    mode = request.json.get('mode', 'default')  # 'analyze' or 'default'

    global script_prompt
    full_prompt = f"{script_prompt}\n\n{user_message}"
    result = ask_llama(full_prompt, mode)
    return jsonify(result)

