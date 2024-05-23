var socket = new WebSocket('http://localhost:3000/');

    socket.onmessage = function(event) {
        var message = JSON.parse(event.data);
        displayMessage(message.sender, message.text);
    };

    function toggleChat() {
        var chatBody = document.getElementById('chat-body');
        if (chatBody.style.display === 'none') {
            chatBody.style.display = 'block';
        } else {
            chatBody.style.display = 'none';
        }
    }

    function sendMessage(event) {
        if (event.key === 'Enter') {
            var messageInput = document.getElementById('message-input');
            var message = messageInput.value;
            if (message.trim()) {
                displayMessage('You', message);
                messageInput.value = '';
                socket.send(JSON.stringify({ text: message }));
            }
        }
    }

    function displayMessage(sender, message) {
        var messagesDiv = document.getElementById('messages');
        var messageDiv = document.createElement('div');
        messageDiv.textContent = sender + ': ' + message;
        messagesDiv.appendChild(messageDiv);
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
    }