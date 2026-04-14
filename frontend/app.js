/* ============================================================
   Weather Agent Chat - Frontend JavaScript
   ============================================================ */

const BACKEND_URL = 'http://localhost:8001';
const CHAT_ENDPOINT = `${BACKEND_URL}/chat`;

// DOM Elements
const chatArea = document.getElementById('chatArea');
const messageInput = document.getElementById('messageInput');
const sendButton = document.getElementById('sendButton');
const statusIndicator = document.getElementById('statusIndicator');

// Chat State
let chatHistory = [];
let isWaitingForResponse = false;

/* ============================================================
   Initialization
   ============================================================ */

document.addEventListener('DOMContentLoaded', () => {
    // Event Listeners
    sendButton.addEventListener('click', sendMessage);
    messageInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    // Check backend connectivity on startup
    checkBackendStatus();
});

/* ============================================================
   Main Chat Functions
   ============================================================ */

/**
 * Send a message to the backend and display response
 */
async function sendMessage() {
    const message = messageInput.value.trim();

    if (!message) return;
    if (isWaitingForResponse) return;

    try {
        // Clear input immediately
        messageInput.value = '';
        messageInput.focus();

        // Display user message
        displayUserMessage(message);

        // Add to chat history
        chatHistory.push({
            role: 'user',
            content: message
        });

        // Show loading indicator
        setLoading(true);
        displayLoadingMessage();

        // Send to backend
        const response = await fetchChatResponse(message);

        // Remove loading message
        removeLoadingMessage();

        // Display agent response
        displayAgentMessage(response);

        // Add to chat history
        chatHistory.push({
            role: 'assistant',
            content: response
        });

        // Auto-scroll to latest message
        scrollToBottom();

    } catch (error) {
        removeLoadingMessage();
        handleError(error);
    } finally {
        setLoading(false);
    }
}

/**
 * Fetch response from backend
 */
async function fetchChatResponse(message) {
    const payload = {
        query: message,
        chat_history: chatHistory.slice(0, -1) // Exclude the current user message
    };

    const response = await fetch(CHAT_ENDPOINT, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload)
    });

    if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(
            errorData.error ||
            `Backend error: ${response.status} ${response.statusText}`
        );
    }

    const data = await response.json();
    
    if (!data.response) {
        throw new Error('Empty response from backend');
    }

    return data.response;
}

/**
 * Check if backend is accessible
 */
async function checkBackendStatus() {
    try {
        const response = await fetch(`${BACKEND_URL}/health`, {
            method: 'GET',
            headers: { 'Content-Type': 'application/json' }
        });

        if (response.ok) {
            console.log('✅ Backend is online and ready');
            showStatus('Connected to backend', 'success');
        } else {
            showStatus('Backend unreachable', 'error');
        }
    } catch (error) {
        console.warn('⚠️ Backend connection failed:', error.message);
        showStatus('Unable to connect to backend', 'error');
    }
}

/* ============================================================
   UI Display Functions
   ============================================================ */

/**
 * Display user message in chat
 */
function displayUserMessage(text) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message user';

    const bubble = document.createElement('div');
    bubble.className = 'message-bubble';
    bubble.textContent = text;

    messageDiv.appendChild(bubble);
    chatArea.appendChild(messageDiv);

    // Remove welcome message if it's the first message
    removeWelcomeMessage();
}

/**
 * Display agent message in chat
 */
function displayAgentMessage(text) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message agent';

    const bubble = document.createElement('div');
    bubble.className = 'message-bubble';
    
    // Parse and format the response
    bubble.innerHTML = formatResponseText(text);

    messageDiv.appendChild(bubble);
    chatArea.appendChild(messageDiv);
}

/**
 * Display loading (thinking) indicator
 */
function displayLoadingMessage() {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message agent loading';
    messageDiv.id = 'loadingMessage';

    const bubble = document.createElement('div');
    bubble.className = 'message-bubble';

    const loadingText = document.createElement('span');
    loadingText.textContent = 'Thinking';

    const dots = document.createElement('div');
    dots.className = 'loading-dots';
    dots.innerHTML = '<span class="loading-dot"></span><span class="loading-dot"></span><span class="loading-dot"></span>';

    bubble.appendChild(loadingText);
    bubble.appendChild(dots);
    messageDiv.appendChild(bubble);
    chatArea.appendChild(messageDiv);
}

/**
 * Remove loading message
 */
function removeLoadingMessage() {
    const loading = document.getElementById('loadingMessage');
    if (loading) {
        loading.remove();
    }
}

/**
 * Remove welcome message
 */
function removeWelcomeMessage() {
    const welcome = chatArea.querySelector('.welcome-message');
    if (welcome) {
        welcome.remove();
    }
}

/**
 * Format response text with basic markdown support
 */
function formatResponseText(text) {
    // Escape HTML
    let formatted = text
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;');

    // Bold text: **text** -> <strong>text</strong>
    formatted = formatted.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');

    // Line breaks
    formatted = formatted.replace(/\n/g, '<br>');

    return formatted;
}

/* ============================================================
   Status & Error Handling
   ============================================================ */

/**
 * Show status indicator
 */
function showStatus(message, type = 'info') {
    statusIndicator.textContent = message;
    statusIndicator.className = `status-indicator status-${type}`;

    if (type === 'success') {
        statusIndicator.style.display = 'flex';
        setTimeout(() => {
            statusIndicator.style.display = 'none';
        }, 3000);
    } else if (type === 'error') {
        statusIndicator.style.display = 'flex';
        // Keep error displayed
    }
}

/**
 * Handle and display errors gracefully
 */
function handleError(error) {
    console.error('❌ Chat Error:', error);

    const errorMessage = error.message || 'An unexpected error occurred';

    // Display error in chat
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message error';

    const bubble = document.createElement('div');
    bubble.className = 'message-bubble';
    bubble.innerHTML = `<strong>⚠️ Error:</strong> ${escapeHtml(errorMessage)}`;

    messageDiv.appendChild(bubble);
    chatArea.appendChild(messageDiv);

    // Show error toast
    showErrorToast(errorMessage);

    // Log for debugging
    console.error('Full error details:', {
        message: errorMessage,
        stack: error.stack,
        timestamp: new Date().toISOString()
    });
}

/**
 * Show error toast notification
 */
function showErrorToast(message) {
    const toast = document.createElement('div');
    toast.className = 'error-toast';
    toast.textContent = `⚠️ ${message}`;
    document.body.appendChild(toast);

    // Auto-remove after 5 seconds
    setTimeout(() => {
        toast.remove();
    }, 5000);
}

/**
 * Escape HTML special characters
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

/* ============================================================
   State Management
   ============================================================ */

/**
 * Set loading state
 */
function setLoading(isLoading) {
    isWaitingForResponse = isLoading;
    messageInput.disabled = isLoading;
    sendButton.disabled = isLoading;

    if (isLoading) {
        sendButton.style.opacity = '0.6';
    } else {
        sendButton.style.opacity = '1';
    }
}

/**
 * Auto-scroll chat to bottom
 */
function scrollToBottom() {
    // Use setTimeout to ensure DOM is updated
    setTimeout(() => {
        chatArea.scrollTop = chatArea.scrollHeight;
    }, 0);
}

/* ============================================================
   Utility Functions
   ============================================================ */

/**
 * Log activity for debugging
 */
function log(level, message, ...args) {
    const timestamp = new Date().toLocaleTimeString();
    console.log(`[${timestamp}] ${level}: ${message}`, ...args);
}

/* ============================================================
   Expose functions for debugging
   ============================================================ */

// Make some functions available in console for debugging
window.chatDebug = {
    getHistory: () => chatHistory,
    clearHistory: () => { chatHistory = []; console.log('Chat history cleared'); },
    parseMessage: (msg) => log('DEBUG', msg),
    backendURL: BACKEND_URL,
    resizeChat: () => chatArea.scrollTop = chatArea.scrollHeight
};

console.log('💬 Weather Agent Chat UI loaded. Type chatDebug.getHistory() to see chat history.');