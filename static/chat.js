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
