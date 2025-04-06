async function sendMessage() {
    const input = document.getElementById("chatInput");
    const message = input.value.trim();
    if (message === "") return;

    displayMessage(message, "alert-secondary");

    try {
        const response = await fetch("http://127.0.0.1:5000/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message: message })
        });

        const data = await response.json();
        
        if (data.reply.error) {
            displayMessage("⚠ 오류: " + data.reply.error, "alert-danger");
        } else {
            const replyText = JSON.stringify(data.reply, null, 2);
            displayMessage(replyText, "alert-primary");
        }
    } catch (error) {
        displayMessage("서버 오류 발생!", "alert-danger");
    }
}

function displayMessage(text, style) {
    const chatBox = document.getElementById("chatMessages");
    const messageElement = document.createElement("div");
    messageElement.classList.add("alert", style);
    messageElement.textContent = text;
    chatBox.appendChild(messageElement);
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