const chatBox = document.getElementById('chat-box');
const chatForm = document.getElementById('chat-form');
const userInput = document.getElementById('user-input');

function addMessage(text, isUser) {
    const div = document.createElement('div');
    div.className = `flex ${isUser ? 'justify-end' : 'justify-start'}`;

    const bubble = document.createElement('div');
    bubble.className = isUser
        ? 'bg-blue-600 text-white px-5 py-3 rounded-2xl rounded-tr-none max-w-xs lg:max-w-md shadow-md'
        : 'bg-gray-700 text-gray-100 px-5 py-3 rounded-2xl rounded-tl-none max-w-xs lg:max-w-md shadow-md whitespace-pre-wrap';

    bubble.textContent = text;
    div.appendChild(bubble);
    chatBox.appendChild(div);
    chatBox.scrollTop = chatBox.scrollHeight;
}

function showLoading() {
    const div = document.createElement('div');
    div.id = 'loading-indicator';
    div.className = 'flex justify-start';
    div.innerHTML = `
        <div class="bg-gray-700 px-4 py-3 rounded-2xl rounded-tl-none shadow-md flex gap-1 items-center">
            <div class="w-2 h-2 bg-gray-400 rounded-full typing-dot"></div>
            <div class="w-2 h-2 bg-gray-400 rounded-full typing-dot"></div>
            <div class="w-2 h-2 bg-gray-400 rounded-full typing-dot"></div>
        </div>
    `;
    chatBox.appendChild(div);
    chatBox.scrollTop = chatBox.scrollHeight;
}

function removeLoading() {
    const loading = document.getElementById('loading-indicator');
    if (loading) loading.remove();
}

chatForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const message = userInput.value.trim();
    if (!message) return;

    addMessage(message, true);
    userInput.value = '';
    showLoading();

    try {
        const response = await fetch('/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message })
        });
        const data = await response.json();
        removeLoading();
        addMessage(data.response, false);
    } catch (error) {
        removeLoading();
        addMessage("Sorry, something went wrong. Please check your connection.", false);
    }
});
