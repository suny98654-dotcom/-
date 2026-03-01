document.addEventListener("DOMContentLoaded", function() {

    const chatButton = document.getElementById("chat-button");
    const chatWindow = document.getElementById("chat-window");
    const closeChat = document.getElementById("close-chat");
    const sendBtn = document.getElementById("send-btn");
    const userInput = document.getElementById("user-input");
    const chatBox = document.getElementById("chat-messages");

    /* 打开窗口 */
    chatButton.onclick = function() {
        chatWindow.style.display = "flex";
    };

    /* 关闭窗口 */
    closeChat.onclick = function() {
        chatWindow.style.display = "none";
    };

    /* 发送消息 */
  function sendMessage() {

    let message = userInput.value.trim();
    if (message === "") return;

    chatBox.innerHTML += `<div class="message user">你：${message}</div>`;
    chatBox.scrollTop = chatBox.scrollHeight;

    userInput.value = "";

    fetch("http://127.0.0.1:8000/chat", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ message: message })
    })
    .then(response => response.json())
    .then(data => {
        chatBox.innerHTML += `<div class="message ai">AI：${data.reply}</div>`;
        chatBox.scrollTop = chatBox.scrollHeight;
    })
    .catch(error => {
        chatBox.innerHTML += `<div class="message ai">AI：连接后端失败。</div>`;
    });
}

    sendBtn.addEventListener("click", sendMessage);

    userInput.addEventListener("keydown", function(e){
        if(e.key === "Enter"){
            sendMessage();
        }
    });

});