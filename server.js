const express = require('express');
const http = require('http');
const WebSocket = require('ws');
const bodyParser = require('body-parser');
const axios = require('axios');
const { log } = require('console');

const app = express();
const server = http.createServer(app);
const wss = new WebSocket.Server({ server });

const TELEGRAM_API_URL = 'https://api.telegram.org/bot6118675762:AAHWsHLQmULD79EV5zHzS7hAFIgXI-E9VbI';
const TELEGRAM_CHAT_ID = '175920432';

app.use(bodyParser.json());

// WebSocket connection handling
wss.on('connection', (ws) => {
    console.log('Client connected');
    
    ws.on('message', (message) => {
        const msgData = JSON.parse(message);
        const userMessage = msgData.text;

        console.log(userMessage);
        // Forward the message to the Telegram bot
        axios.post(`${TELEGRAM_API_URL}/sendMessage`, {
            chat_id: TELEGRAM_CHAT_ID,
            text: userMessage
        }).then(response => {
            // Assuming the bot sends a response back to the server
            const reply = response.data.result.text;
            // ws.send(JSON.stringify({ sender: 'Operator', text: reply }));
        }).catch(error => {
            console.error('Error sending message to Telegram:', error);
        });
    });

    ws.on('close', () => {
        console.log('Client disconnected');
    });
});

// Telegram webhook endpoint to receive messages from the operator
app.post('/webhook', (req, res) => {
    const message = req.body.message;
    const chatId = message.chat.id;
    const text = message.text;
    console.log(message)

    // Broadcast the message to all connected WebSocket clients
    wss.clients.forEach((client) => {
        if (client.readyState === WebSocket.OPEN) {
            client.send(JSON.stringify({ sender: message.from.first_name, text: text }));
        }
    });

    res.sendStatus(200);
});

// Set up your Telegram webhook URL
axios.post(`${TELEGRAM_API_URL}/setWebhook`, {
    url: 'https://dd5c-147-197-250-32.ngrok-free.app/webhook'
}).then(response => {
    console.log('Webhook set:', response.data);
}).catch(error => {
    console.error('Error setting webhook:', error);
});

const PORT = process.env.PORT || 3000;
server.listen(PORT, () => {
    console.log(`Server is running on port ${PORT}`);
});
