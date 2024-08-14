const chatWindow = document.getElementById('chat-window');
const chatForm = document.getElementById('chat-form');
const userInput = document.getElementById('user-input');
let chatHistory = [];

chatForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const message = userInput.value.trim();
    if (!message) return;

    addMessageToChat('user', message);
    userInput.value = '';

    try {
        const response = await fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message, history: chatHistory }),
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        addMessageToChat('bot', data.response);
    } catch (error) {
        console.error('Error:', error);
        addMessageToChat('bot', 'Sorry, there was an error processing your request.');
    }
});

function addMessageToChat(role, content) {
    console.log(`Adding ${role} message:`, content);
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role === 'user' ? 'user-message' : 'bot-message'}`;
    messageDiv.innerHTML = marked.parse(content);
    chatWindow.appendChild(messageDiv);
    chatWindow.scrollTop = chatWindow.scrollHeight;

    chatHistory.push({ [role]: content });
    console.log('Current chat history:', chatHistory);
}

// Add this line to check if the script is loaded
console.log('Chat script loaded');