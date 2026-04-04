async function sendMessage() {
    const input = document.getElementById('user-input');
    const chatBox = document.getElementById('chat-box');
    const message = input.value.trim();

    if (message === "") return;

    // إضافة رسالة المستخدم
    chatBox.innerHTML += `<div class="message user-msg">${message}</div>`;
    input.value = "";
    
    // إضافة رسالة مؤقتة للـ AI
    const loadingId = "loading-" + Date.now();
    chatBox.innerHTML += `<div id="${loadingId}" class="message ai-msg">جاري التفكير...</div>`;
    chatBox.scrollTop = chatBox.scrollHeight;

    try {
        const response = await fetch('http://127.0.0.1:8000/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                user_id: "Ahmed_123", // هنا ممكن تستخدم ID اليوزر الحقيقي من السيستم
                prompt: message
            })
        });

        const data = await response.json();
        
        // حذف رسالة "جاري التفكير" ووضع الرد الحقيقي
        document.getElementById(loadingId).innerText = data.answer;
        chatBox.scrollTop = chatBox.scrollHeight;

    } catch (error) {
        document.getElementById(loadingId).style.color = "red";
        document.getElementById(loadingId).innerText = "عذراً، تعذر الاتصال بالسيرفر.";
    }
}

// دالة الضغط على Enter
function handleKeyPress(event) {
    if (event.key === 'Enter') {
        sendMessage();
    }
}
