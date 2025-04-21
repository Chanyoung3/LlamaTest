function setData(e) {
    e.preventDefault();  // 기본 제출 방지

    const fileInput = document.getElementById("data-upload");
    const file = fileInput.files[0];

    if (!file) {
        alert("파일을 선택해주세요.");
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
            sessionStorage.setItem("llama_result", data.preview);
            sessionStorage.setItem("llama_file_url", data.file_url);
            window.location.href = "/result";  // result.html 페이지로 이동
        } else {
            alert("오류 발생: " + data.error);
        }
    })
    .catch(err => {
        console.error("업로드 실패:", err);
        alert("파일 업로드 중 오류 발생");
    });
}
