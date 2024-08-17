function initChatWidget(shadow) {
    var chatInput = shadow.getElementById('message-input');
    var sendBtn = shadow.getElementById("send-button")
    const HOST = "http://127.0.0.1:3000";
    let socket = io.connect(HOST)

    // WebSocket event listeners for better debugging
    socket.on('connect', () => {
        console.log('WebSocket connected');
    });

    socket.on('disconnect', (reason) => {
        console.log('WebSocket disconnected:', reason);
    });

    socket.on('reconnect_attempt', () => {
        console.log('WebSocket reconnect attempt');
    });

    socket.on('error', (error) => {
        console.error('WebSocket error:', error);
    });

    // Sound notification setup
    const messageSound = new Audio(`${HOST}/sounds/pop.mp3`);
    messageSound.volume = 0.5; // Adjust the volume if needed

    chatConfig = JSON.parse(localStorage.getItem("chatConfig"))
    // console.log(chatConfig)

    console.log("Loaded!!!")

    socket.on('client_registered', function(data) {
        console.log('Client registered with ID:', data);
    });

    socket.on("message", (msg)=>{
        displayReceivedMessage(msg.sender, msg.text);
        messageSound.play()
    })

    chatInput.addEventListener('keypress', function(event) {
        if (event.key === 'Enter') {
            var message = chatInput.value;
            if (message.trim()) {
                displaySentMessage(message);
                chatInput.value = '';
                socket.emit('message', { type: 'message', text: message, chatId: chatConfig.id, chatName: chatConfig.chatName });
            }
        }
    });

    sendBtn.addEventListener('click', (e)=>{
            var message = chatInput.value;
            if (message.trim()) {
                displaySentMessage(message);
                chatInput.value = '';
                socket.emit('message', { type: 'message', text: message, chatId: chatConfig.id, chatName: chatConfig.chatName });
            }
    })

    shadow.getElementById("file-input").addEventListener('change', (e) => uploadFile(e));

    function uploadFile(e) {
        e.preventDefault();
        let file = e.target.files[0];

        if (!file) {
            return;
        }
        if (file.size > 10000000) { // File size limit 10MB
            alert('File should be smaller than 10MB');
            return;
        }

        var reader = new FileReader();
        var rawData = new ArrayBuffer();

        reader.onload = function (e) {
            rawData = e.target.result;
            console.log('File loaded:', file.name, file.type);
            socket.emit("message", {
                type: 'attachment',
                data: rawData,
                chatId: chatConfig.id,
                chatName: chatConfig.chatName,
                filename: file.name,
                mimetype: file.type
            });
            console.log("Message sent with file:", file.name);
        };

        reader.onerror = function (e) {
            console.error('Error reading file:', e);
        };

        reader.readAsArrayBuffer(file);
        
        if (file.type.startsWith('image/')) {
            displayUploadedPhoto(URL.createObjectURL(file), file.name);
        } else {
            // displayUploadedFile(file.name, file.type);
            console.log('x3')
        }
    }


    function displayReceivedMessage(sender, message) {
        var messagesDiv = shadow.getElementById('window-content');
        messagesDiv.innerHTML += `
        <div class="message sender">
            <div class="message-wrapper">
                <p class="sender-name">${sender}</p>
                <p class="date sender">${getCurrentDateTime()}</p>
            </div>
            <p class="message-text">${message}</p>
        </div>
        `

        if (!isFloatingButtonHidden(shadow)) {
            const notifier = shadow.getElementById('notifier');
            notifier.style.display = 'block';
        }
    }

    function displaySentMessage(message) {
        var messagesDiv = shadow.getElementById('window-content');
        messagesDiv.innerHTML += `
        <div class="message receiver">
            <div class="message-wrapper">
                <p class="receiver-name">Me</p>
                <p class="date receiver">${getCurrentDateTime()}</p>
            </div>
            <p class="message-text">${message}</p>
        </div>
        `
    }

    function displayUploadedPhoto(fileUrl, fileName) {
        var messagesDiv = shadow.getElementById('window-content');
        messagesDiv.innerHTML += `
        <div class="message receiver">
            <div class="message-wrapper">
                <p class="receiver-name">Me</p>
                <p class="date receiver">${getCurrentDateTime()}</p>
            </div>
            <img src="${fileUrl}" alt="${fileName}" class="message-text">
        </div>
        `
    }

    function isFloatingButtonHidden() {
        const floatingButton = shadow.getElementById('floating-button');
        const computedStyle = getComputedStyle(floatingButton);
        return computedStyle.display === 'none';
    }
    

    // Function to get current date and time in the specified format
    function getCurrentDateTime() {
        // Array of month names in Russian
        const monthNames = ['января', 'февраля', 'марта', 'апреля', 'мая', 'июня', 'июля', 'августа', 'сентября', 'октября', 'ноября', 'декабря'];
        
        // Create a new Date object
        const now = new Date();
        
        // Extract the day, month, hours, and minutes
        const day = now.getDate();
        const month = monthNames[now.getMonth()];
        const hours = now.getHours().toString().padStart(2, '0');
        const minutes = now.getMinutes().toString().padStart(2, '0');
        
        // Format the date and time
        const formattedDateTime = `${day} ${month} ${hours}:${minutes}`;
        
        return formattedDateTime;
    }
}