var chatInput = document.getElementById('message-input');
var sendBtn = document.getElementById("send-button")
let socket = io.connect("http://localhost:3000/")

chatConfig = JSON.parse(localStorage.getItem("chatConfig"))
// console.log(chatConfig)

console.log("Loaded!!!")

socket.on('client_registered', function(data) {
    console.log('Client registered with ID:', data);
});

socket.on("message", (msg)=>{
    displayReceivedMessage(msg.sender, msg.text);
})

chatInput.addEventListener('keypress', function(event) {
    if (event.key === 'Enter') {
        var messageInput = document.getElementById('message-input');
        var message = messageInput.value;
        if (message.trim()) {
            displaySentMessage(message);
            messageInput.value = '';
            socket.emit('message', { type: 'message', text: message, chatId: chatConfig.id, chatName: chatConfig.chatName });
        }
    }
});

sendBtn.addEventListener('click', (e)=>{
    var messageInput = document.getElementById('message-input');
        var message = messageInput.value;
        if (message.trim()) {
            displaySentMessage(message);
            messageInput.value = '';
            socket.emit('message', { type: 'message', text: message, chatId: chatConfig.id, chatName: chatConfig.chatName });
        }
})

document.getElementById("file-input").addEventListener('change', (e)=>uploadFile(e))

function uploadFile(e) {
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
        socket.emit("message", {
            type: 'attachment',
            data: rawData,
            chatId: chatConfig.id, 
            chatName: chatConfig.chatName,
            filename: file.name,
            mimetype: file.type
        });
    };
    reader.readAsArrayBuffer(file);
    displayUploadedPhoto(URL.createObjectURL(file), file.name)
}


function displayReceivedMessage(sender, message) {
    var messagesDiv = document.getElementById('window-content');
    messagesDiv.innerHTML += `
    <div class="message sender">
        <div class="message-wrapper">
            <p class="sender-name">${sender}</p>
            <p class="date sender">${getCurrentDateTime()}</p>
        </div>
        <p class="message-text">${message}</p>
    </div>
    `
}

function displaySentMessage(message) {
    var messagesDiv = document.getElementById('window-content');
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
    var messagesDiv = document.getElementById('window-content');
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
