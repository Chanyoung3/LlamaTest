from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import requests
import json

app = Flask(__name__)
CORS(app)  # CORS 허용

# HTML 페이지 제공
@app.route("/")
def home():
    return render_template("index.html")

OLLAMA_API_URL = "http://localhost:11434/api/generate"

def ask_llama(conversation):
    payload = {
        "model": "llama3.1:latest",
        "prompt": f"{conversation}",
        "stream": False
    }
    response = requests.post(OLLAMA_API_URL, json=payload)
    if response.status_code == 200:
        return response.json().get("response", "").strip()
    else:
        return {"error": response.status_code, "message": response.text}

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_message = data.get("message", "")

    if not user_message:
        return jsonify({"error": "Empty message"}), 400

    response = ask_llama(user_message)
    return jsonify({"reply": response})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
