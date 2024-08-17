(function() {
    const HOST = "http://5.101.7.211";
    var newDiv = document.createElement('div');
    newDiv.id = 'chat-widget';
    document.body.appendChild(newDiv);

    var chatConfig = {};
    var userCode = window.userCode;  // This should be passed from the HTML where the script is included

    function openWindow(shadow) {
        shadow.getElementById('custom-window').style.right = '0';
        shadow.getElementById('floating-button').style.display = 'none';
        shadow.getElementById('notifier').style.display = 'none';
    }
    
    function closeWindow(shadow) {
        shadow.getElementById('custom-window').style.right = '-450px';
        shadow.getElementById('floating-button').style.display = 'flex';
    }
    
    function handleFileUpload(event) {
        const fileInput = event.target;
        const files = fileInput.files;
        if (files.length > 0) {
            // Handle the uploaded file(s)
            console.log('File(s) uploaded:', files);
            // You can process the files here, e.g., display file names, upload to server, etc.
        }
    }

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

    function loadScript(url, callback) {
        var script = document.createElement('script');
        script.src = url;
        script.async = true;
        script.onload = callback;
        document.head.appendChild(script);
    }

    fetch(`${HOST}/get_chat_config?user_code=` + userCode)
        .then(response => response.json())
        .then(config => {
            if (config.error) {
                console.error(config.error);
            } else {
                console.log(`Subscription status: ${config.subscriptionStatus}`);
                chatConfig = config;
                localStorage.setItem("chatConfig", JSON.stringify(config));
                
                // Create shadow root
                var widgetFrame = document.getElementById('chat-widget');
                var shadow = widgetFrame.attachShadow({ mode: 'open' });

                shadow.innerHTML = `
                    <title>Nimpo Widget</title>
                    <link rel="stylesheet" type="text/css" href="${HOST}/styles/styles.css"> 
                    
                    <div id="floating-button" class="floating-button">
                        <img src="${HOST}/img/nimpo-icon.svg" alt="Call Icon" class="nimpo-icon">
                        <div id="notifier" class="notifier" style="display: none;"></div>
                    </div>
                    <div id="custom-window" class="custom-window">
                        <div class="window-header wrapper">
                            <img src="${HOST}/img/company-logo.svg" alt="Logo" class="header-logo">
                            <div class="header-text">
                                <h2 class="company-name">${chatConfig.chatName}</h2>
                                <p class="description">${chatConfig.description}</p>
                            </div>
                            <button id="close-button">&#10005;</button> <!-- X icon -->
                        </div>
                
                        <div class="wrapper" id="window-content">
                            <div class="message sender">
                                <div class="message-wrapper">
                                    <p class="sender-name">Sender</p>
                                    <p class="date sender">${getCurrentDateTime()}</p>
                                </div>
                                <p class="message-text">${chatConfig.greeting}</p>
                            </div>
                        </div>
                
                        <div class="window-footer">
                            <div class="input-area wrapper">
                                <button class="attach-button" id="attach-btn">
                                    <img src="${HOST}/img/attach-icon.svg" alt="Attach Icon">
                                </button>
                                <input type="file" id="file-input" accept="image/*" style="display: none;">
                                <input type="text" id="message-input" placeholder="Введите свое сообщение...">
                                <button id="send-button"><img src="${HOST}/img/send-button.svg" alt="Send Icon"></button>
                            </div>
                            <hr class="footer-line">
                            <div class="nimpo-power wrapper">
                                <p>powered by</p>
                                <a href="http://nimpo.uz/" class="nimpo-link">
                                    <img src="${HOST}/img/nimpo-logo-text.svg" alt="Nimpo Logo">
                                </a>
                            </div>
                        </div>
                    </div>
                `;

                // Attach event listeners inside the shadow DOM
                shadow.getElementById("attach-btn").addEventListener('click', () => shadow.getElementById('file-input').click())
                shadow.getElementById("floating-button").addEventListener('click', () => openWindow(shadow));
                shadow.getElementById("close-button").addEventListener('click', () => closeWindow(shadow));
                shadow.getElementById("file-input").addEventListener('change', handleFileUpload);

                // Load the scripts after the DOM is ready
                loadScript("https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.7.5/socket.io.js", () => {
                    loadScript(`${HOST}/js/script.js`, () => {
                        // Ensure that script.js can access elements inside the shadow DOM
                        if (typeof window.initChatWidget === 'function') {
                            window.initChatWidget(shadow);
                        }
                    });
                });
            }
        })
        .catch(error => console.error('Error fetching chat config:', error));
})();
