from flask import Flask, request, jsonify
from flask_socketio import SocketIO
import requests
import asyncio
import websockets
import json
import threading
import telebot
from telebot import types
import uuid
from db import DB
from flask_cors import CORS


app = Flask(__name__)
CORS(app)
# socketio = SocketIO(app)

# TELEGRAM_API_URL = 'https://api.telegram.org/bot1443244805:AAHmStbxNHKWgC--pC-IR-DHO6FDs9loMhw'
bot = telebot.TeleBot('1443244805:AAHmStbxNHKWgC--pC-IR-DHO6FDs9loMhw')
db = DB()
shutdown_event = threading.Event()
# chat_configs = {}

# WebSocket server handling
connected_clients = {}

async def websocket_handler(websocket, path):
    client_id = str(uuid.uuid4())
    connected_clients[client_id] = websocket
    print(f"Client {client_id} connected")

    try:
        async for message in websocket:
            if shutdown_event.is_set():
                break
            msg_data = json.loads(message)
            user_message = msg_data['text']
            chat_id = msg_data['id']
            print(f"Received message from {client_id}: {user_message}")

            # Forward the message to the Telegram bot
            try:
                markup = types.InlineKeyboardMarkup(row_width=2)
                info = types.InlineKeyboardButton("info", callback_data=f"_info_{client_id}")
                reply = types.InlineKeyboardButton("reply", callback_data=f"_reply_{client_id}")
                markup.add(info, reply)

                chat_config = db.getChatConfig(chat_id)
                if chat_config:
                    for operator_username, operator_chat_id in chat_config['operators']:
                        bot.send_message(operator_chat_id, user_message, reply_markup=markup)
                else:
                    print(f"Chat configuration not found for chat_id: {chat_id}")
            
            except Exception as e:
                print('Error sending message to Telegram:', e)

    finally:
        print(f"Client {client_id} disconnected")
        del connected_clients[client_id]

@bot.callback_query_handler(func=lambda callback: True)
def handle_callback_query(callback):
    callback_data = callback.data.split('_')
    if len(callback_data) > 2:
        action = callback_data[1]
        client_id = callback_data[2]

        if action == "reply":
            msg = bot.send_message(callback.message.chat.id, "Your message:")
            bot.register_next_step_handler(msg, lambda message: process_reply(message, client_id))

def process_reply(message, client_id):
    asyncio.run(send_message_to_client({
        'sender': message.from_user.first_name,
        'text': message.text
    }, client_id))

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        "Welcome! Use /setup to configure your chat widget.\n"
        "Commands:\n"
        "/setup - Set up chat name and description\n"
        "/operators - Add operators\n"
        "/join - Join chat as operator\n"
        "/code - Get widget code"
    )

# Command to add operators
@bot.message_handler(commands=['operators'])
def add_operator(message):
    chat_id = message.chat.id

    msg = bot.send_message(chat_id, "Enter the operator's Telegram username (without @):")
    bot.register_next_step_handler(msg, process_operator_step)

def process_operator_step(message):
    chat_id = message.chat.id
    operator_username = message.text
    
    db.addOperatorToChat(chat_id, operator_username)
    bot.send_message(chat_id, f"Operator @{operator_username} added.\n{chat_id} - is code for your chat. Give this code to your operators. \nAdd another with /operators or get widget code with /code.\nJoin chat as an operator with /join")

@bot.message_handler(commands=['join'])
def joinChatAsOperator(message):
    msg = bot.send_message(message.chat.id, "Enter chat code you want to enter as an operator.")
    bot.register_next_step_handler(msg, joinChatAsOperatorHandler)

def joinChatAsOperatorHandler(message):
    chatId = message.chat.id
    username = message.chat.username
    toJoin = int(message.text)
    chat_operators = db.chatsCollection.find_one({"_id": toJoin})['operators'].keys()

    if(username in chat_operators):
        db.updateOperatorInChat(toJoin, username, chatId)
        bot.send_message(chatId, "You successfully joined as an operator.\nNow all incoming messages will directed to you.")
    else:
        bot.send_message(chatId, "You were not added as an operator to this chat.")

# Command to set up chat widget
@bot.message_handler(commands=['setup'])
def setup(message):
    chat_id = message.chat.id
    username = message.chat.username
    db.addAdmin(chat_id, username)

    msg = bot.send_message(chat_id, "Enter the chat name:")
    bot.register_next_step_handler(msg, process_chat_name_step)

def process_chat_name_step(message):
    chat_id = message.chat.id
    chat_name = message.text

    db.updateChatName(chat_id, chat_name)
    msg = bot.send_message(chat_id, "Enter the chat description:")
    bot.register_next_step_handler(msg, process_chat_description_step)

def process_chat_description_step(message):
    chat_id = message.chat.id
    chat_desc = message.text

    db.updateChatDescription(chat_id, chat_desc)
    bot.send_message(chat_id, "Chat setup complete. Use /operators to add operators.")


# Command to get widget code
@bot.message_handler(commands=['code'])
def get_widget_code(message):
    chat_id = message.chat.id
    chat_config = db.getChatConfig(chat_id)

    if chat_config:
        unique_code = chat_config['unique_code']
        widget_code = f"""
        <div id="chat-widget"></div>
        <script>
        var userCode = '{unique_code}';
        (function() {{
            var script = document.createElement('script');
            script.src = "./client.js";
            document.head.appendChild(script);
        }})();
        </script>
        """
        bot.send_message(chat_id, "Paste the following code into your website:")
        bot.send_message(chat_id, f"```html\n{widget_code}\n```", parse_mode='Markdown')
    else:
        bot.send_message(chat_id, "Chat not set up. Please use /setup to set up the chat.")













async def send_message_to_client(message, target_client_id):
    if target_client_id in connected_clients:
        client = connected_clients[target_client_id]
        if client.open:
            await client.send(json.dumps(message))
    else:
        print(f"Client {target_client_id} not connected")


@app.route('/get_chat_config', methods=['GET'])
def get_chat_config():
    user_code = request.args.get('user_code')

    chat = db.getChatByCode(user_code)
    if chat:
        return jsonify({
            'chatName': chat.get('chat_name', 'Default Chat Name'),
            'description': chat.get('description', 'Default Description'),
            'subscriptionStatus': 'active'  # Replace with actual subscription check
        })
    
    return jsonify({'error': 'Chat config not found'}), 404

@app.after_request
def after_request(response):
    response.headers.set('Access-Control-Allow-Origin', '*')
    response.headers.set('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.set('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response 


# Function to start the WebSocket server

async def websocket_server():
    server = await websockets.serve(websocket_handler, "localhost", 3001)
    await shutdown_event.wait()
    server.close()
    await server.wait_closed()

def start_websocket_server():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(websocket_server())

def start_telegram_bot():
    bot.polling(none_stop=True)

def start_api_server():
    app.run(port=5000)

def run_all_servers():
    ws_thread = threading.Thread(target=start_websocket_server)
    bot_thread = threading.Thread(target=start_telegram_bot)
    api_thread = threading.Thread(target=start_api_server)

    ws_thread.start()
    bot_thread.start()
    api_thread.start()

    try:
        ws_thread.join()
        bot_thread.join()
        api_thread.join()
    except KeyboardInterrupt:
        print("Shutdown initiated")
        shutdown_event.set()
        api_thread.join()
        ws_thread.join()
        bot_thread.join()
        print("Shutdown complete")


# Start the WebSocket server in a separate thread
if __name__ == '__main__':
    run_all_servers()