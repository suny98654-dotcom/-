const chatMessages = document.getElementById("chatMessages");
const userInput = document.getElementById("userInput");
const sendButton = document.getElementById("sendButton");

// ===== 添加一条消息到聊天框 =====
function addMessage(role, text) {
    const msgDiv = document.createElement("div");
    msgDiv.className = role === "user"
        ? "message message-user"
        : "message message-ai";

    msgDiv.innerHTML = `
        <div class="message-avatar">
            <span>${role === "user" ? "🧑" : "🌱"}</span>
        </div>
        <div class="message-content">
            <div class="message-sender">
                ${role === "user" ? "我" : "小农助手"}
            </div>
            <div class="message-text">${text}</div>
        </div>
    `;

    chatMessages.appendChild(msgDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    return msgDiv;
}

// ===== 发送消息 =====
async function sendMessage(text) {
    if (!text.trim()) return;

    // 1️⃣ 显示用户消息（右）
    addMessage("user", text);
    userInput.value = "";

    // 2️⃣ 禁用输入 & 按钮（防连点）
    sendButton.disabled = true;
    userInput.disabled = true;

    // 3️⃣ 显示 AI 思考中（左）
    const loadingMsg = addMessage("ai", "🌱 小农助手正在思考…");

    try {
        const res = await fetch("http://127.0.0.1:8000/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message: text })
        });

        const data = await res.json();

        const aiReply = data.reply || "我有点没听清，可以再说一次吗？";

    // 替换思考中内容
    loadingMsg.querySelector(".message-text").innerText = aiReply;

    // ⭐ 食育建议卡片触发条件（核心）
    if (aiReply.length > 60) {
   showFoodCard(extractSummary(aiReply));
    }


    } catch (err) {
        loadingMsg.querySelector(".message-text").innerText =
            "⚠️ 网络有点不稳定，我们再试一次吧";
        console.error(err);
    }

    // 5️⃣ 恢复输入
    sendButton.disabled = false;
    userInput.disabled = false;
    userInput.focus();
}

// ===== 点击发送 =====
sendButton.addEventListener("click", () => {
    sendMessage(userInput.value);
});

// ===== Enter 发送 =====
userInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        sendMessage(userInput.value);
    }
});

// ===== 快捷问题 =====
document.querySelectorAll(".quick-action-btn").forEach(btn => {
    btn.addEventListener("click", () => {
        sendMessage(btn.dataset.question);
    });
});

const clearChatBtn = document.getElementById("clearChat");

// ===== 初始欢迎语 =====
function showWelcomeMessage() {
    addMessage(
        "ai",
        `你好～我是 <strong>小农助手</strong> 🌱<br><br>
        最近很多人都在问我这些：<br><br>
        👉 <span class="suggestion">现在适合吃什么当季蔬菜？</span><br>
        👉 <span class="suggestion">普通家庭怎么吃得健康又省钱？</span><br>
        👉 <span class="suggestion">农产品怎么保存不浪费？</span><br><br>
        你也可以直接打字问我 😊`
    );
}


// ===== 清空对话 =====
clearChatBtn.addEventListener("click", () => {
    if (!confirm("确定要开始新的对话吗？")) return;

    chatMessages.innerHTML = "";
    showWelcomeMessage();
});

document.querySelectorAll(".quick-action-btn").forEach(btn => {
    btn.addEventListener("click", () => {
        const question = btn.dataset.question;
        if (!question) return;

        userInput.value = question;
        sendButton.click();
    });
});

// ===== 食育建议卡片 =====
function showFoodCard(text) {
    const card = document.createElement("div");
    card.className = "food-card";

    card.innerHTML = `
        <h4>🌱 今日食育小建议</h4>
        <p>${text.slice(0, 80)}...</p>
        <small>来自小农助手 · 助农食育 AI</small>
    `;

    chatMessages.appendChild(card);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function extractSummary(text) {
    // 简单粗暴但效果很好
    const sentences = text.replace(/\n/g, "").split("。");
    return sentences[0] || "合理搭配饮食，有助于身体健康 🌱";
}
