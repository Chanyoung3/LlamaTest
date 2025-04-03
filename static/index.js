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

async function fileUpload() {
    let fileInput = document.getElementById("fileInput");
    let file = fileInput.files[0];
    if (!file) {
        alert("파일을 선택하세요!");
        return;
    }

    let formData = new FormData();
    formData.append("file", file);

    try {
        let response = await fetch("http://127.0.0.1:5000/upload", {
            method: "POST",
            body: formData
        });

        let result = await response.json();
        displayFile(result.file_url, file.name);
    } catch (error) {
        console.error("파일 업로드 오류:", error);
        alert("파일 업로드에 실패했습니다.");
    }
}

function displayFile(url, fileName) {
    let chatBox = document.getElementById("chatMessages");
    let fileMessage = document.createElement("div");
    fileMessage.classList.add("alert", "alert-info", "mt-1");

    let fileLink = document.createElement("a");
    fileLink.href = url;
    fileLink.textContent = `📁 ${fileName}`;
    fileLink.target = "_blank";

    fileMessage.appendChild(fileLink);
    chatBox.appendChild(fileMessage);
    chatBox.scrollTop = chatBox.scrollHeight;
}
