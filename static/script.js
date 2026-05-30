// ==============================
// THEME TOGGLE
// ==============================
function toggleDarkMode() {
    const body = document.body;
    const themeButton = document.getElementById('theme-toggle');
    const icon = themeButton.querySelector('i');

    if (body.classList.contains('light-theme')) {

        body.classList.remove('light-theme');
        body.classList.add('dark-theme');

        icon.className = 'fas fa-sun';

        // Save theme
        localStorage.setItem('theme', 'dark');

    } else {

        body.classList.remove('dark-theme');
        body.classList.add('light-theme');

        icon.className = 'fas fa-moon';

        // Save theme
        localStorage.setItem('theme', 'light');
    }
}

// ==============================
// LOAD SAVED THEME
// ==============================
window.onload = function () {

    const savedTheme = localStorage.getItem('theme');

    const body = document.body;
    const icon = document.querySelector('#theme-toggle i');

    if (savedTheme === 'dark') {

        body.classList.remove('light-theme');
        body.classList.add('dark-theme');

        if (icon) {
            icon.className = 'fas fa-sun';
        }

    } else {

        body.classList.remove('dark-theme');
        body.classList.add('light-theme');

        if (icon) {
            icon.className = 'fas fa-moon';
        }
    }
};

// ==============================
// APPEND CHAT MESSAGE
// ==============================
function appendMessage(message, sender) {

    const chatBox = document.getElementById('chat-box');

    const messageEl = document.createElement('div');

    messageEl.classList.add('message', sender);

    if (sender === 'bot') {
        messageEl.innerHTML = message;
    } else {
        messageEl.textContent = message;
    }

    chatBox.appendChild(messageEl);

    chatBox.scrollTop = chatBox.scrollHeight;
}

// ==============================
// SHOW TYPING ANIMATION
// ==============================
function showTyping() {

    const chatBox = document.getElementById('chat-box');

    const typingEl = document.createElement('div');

    typingEl.classList.add('message', 'bot');

    typingEl.id = 'typing';

    typingEl.textContent = 'Typing...';

    chatBox.appendChild(typingEl);

    chatBox.scrollTop = chatBox.scrollHeight;
}

// ==============================
// REMOVE TYPING
// ==============================
function removeTyping() {

    const typingEl = document.getElementById('typing');

    if (typingEl) {
        typingEl.remove();
    }
}

// ==============================
// SEND MESSAGE
// ==============================
function sendMessage() {

    const input = document.getElementById('msg');

    const message = input.value.trim();

    if (!message) {
        return;
    }

    // User message
    appendMessage(message, 'user');

    input.value = '';

    // Show typing
    showTyping();

    fetch('/chat', {

        method: 'POST',

        headers: {
            'Content-Type': 'application/json'
        },

        body: JSON.stringify({
            message
        })
    })

    .then(response => response.json())

    .then(data => {

        removeTyping();

        const botResponse =
            data.response ||
            'Sorry, I could not process that request.';

        appendMessage(botResponse, 'bot');
    })

    .catch(() => {

        removeTyping();

        appendMessage(
            'Sorry, I could not reach the chatbot service.',
            'bot'
        );
    });
}

// ==============================
// QUICK BUTTONS
// ==============================
function quick(text) {

    const input = document.getElementById('msg');

    input.value = text;

    sendMessage();
}

// ==============================
// ENTER KEY SUPPORT
// ==============================
document
    .getElementById('msg')
    .addEventListener('keypress', function (e) {

        if (e.key === 'Enter') {
            sendMessage();
        }
    });