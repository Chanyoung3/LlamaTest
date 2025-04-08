async function sendMessage() {
    const input = document.getElementById("chatInput");
    const message = input.value.trim();
    if (message === "") return;

    displayMessage(message, "user");
    input.value = "";

    try {
        const response = await fetch("http://127.0.0.1:5000/llama-analyze", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                message: message,
                mode: "default"
            })
        });

        const data = await response.json();

        if (data.error) {
            displayMessage("⚠ 오류: " + data.error, "llama");
        } else {
            const replyText = data.response || JSON.stringify(data, null, 2);

            displayMessage(replyText, "llama");
        }
    } catch (error) {
        displayMessage("서버 오류 발생! " + error.message, "llama");
    }
}


function displayMessage(text, sender = 'user') {
    const chatBox = document.getElementById("chatMessages");

    const messageWrapper = document.createElement("div");
    const senderLabel = document.createElement("small");
    const messageElement = document.createElement("div");

    messageWrapper.classList.add("d-flex", "mb-2", "flex-column");
    senderLabel.classList.add("fw-bold", "mb-1");
    messageElement.classList.add("p-2", "rounded", "shadow-sm");
    messageElement.style.display = "inline-block";
    messageElement.style.maxWidth = "75%";
    messageElement.style.wordBreak = "break-word";

    if (sender === 'user') {
        messageWrapper.classList.add("align-items-end");
        senderLabel.textContent = "나";
        messageElement.classList.add("bg-primary", "text-white");
    } else {
        messageWrapper.classList.add("align-items-start");
        senderLabel.textContent = "LLaMA";
        messageElement.classList.add("bg-light", "text-dark");
    }

    messageElement.textContent = text;

    messageWrapper.appendChild(senderLabel);
    messageWrapper.appendChild(messageElement);
    chatBox.appendChild(messageWrapper);
    chatBox.scrollTop = chatBox.scrollHeight;
}

function handleKeyPress(event) {
    if (event.key === "Enter") {
        sendMessage();
    }
}

function setScript(){
    const fileInput = document.getElementById("excel-upload");
    const file = fileInput.files[0];
  
    if (!file) {
      alert("엑셀 파일을 선택해주세요.");
      return;
    }
  
    const formData = new FormData();
    formData.append("script", file);
  
    fetch("/upload-script", {
      method: "POST",
      body: formData
    })
    .then(res => res.json())
    .then(data => {
      alert("스크립트가 저장되었습니다!");
      console.log("스크립트 내용:", data);
    })
    .catch(err => {
      console.error("업로드 오류:", err);
      alert("스크립트 업로드 실패");
    });
}

function setData() {
    const fileInput = document.getElementById("data-upload");
    const file = fileInput.files[0];

    if (!file) {
        alert("데이터를 선택해주세요.");
        return;
    }

    const formData = new FormData();
    formData.append("data", file);

    fetch("/data-script", {
        method: "POST",
        body: formData
    })
    .then(res => res.json())
    .then(data => {
        if (data.status === "success") {
            displayMessage(`🧾 분석 미리보기:\n${data.preview}`, "llama");

            const downloadLink = document.createElement("a");
            downloadLink.href = data.file_url;
            downloadLink.download = "result.txt";
            downloadLink.textContent = "분석 결과 파일 다운로드";
            downloadLink.className = "btn btn-sm btn-success mt-2";

            const container = document.createElement("div");
            container.appendChild(downloadLink);
            document.getElementById("chatMessages").appendChild(container);
        } else if (data.error) {
            displayMessage(`❌ 오류: ${data.error}`, "alert-danger");
        } else {
            displayMessage("⚠️ 알 수 없는 응답 형식", "alert-warning");
        }
    })
    .catch(err => {
        console.error("업로드 오류:", err);
        alert("데이터 업로드 실패");
        displayMessage("❌ 상담 데이터 업로드 중 오류 발생!", "alert-danger");
    });
}