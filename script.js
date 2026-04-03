async function sendMessage() {
    const input = document.getElementById('user-input');
    const chatBox = document.getElementById('chat-box');
    const message = input.value.trim();

    if (message === "") return;

    chatBox.innerHTML += `<div class="message user-msg">${message}</div>`;
    input.value = "";
    chatBox.scrollTop = chatBox.scrollHeight;

    try {
        const response = await fetch('http://127.0.0.1:8000/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                user_id: "123",
                prompt: message
            })
        });

        const data = await response.json();

        chatBox.innerHTML += `<div class="message ai-msg">${data.answer}</div>`;
        chatBox.scrollTop = chatBox.scrollHeight;

    } catch (error) {
        chatBox.innerHTML += `<div class="message ai-msg" style="color:red">
            السيرفر مش شغال حالياً
        </div>`;
    }
}
