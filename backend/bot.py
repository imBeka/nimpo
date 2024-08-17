import requests
import telebot
from telebot import types
from shared import send_message_to_client
from db import DB
import markups as nav
from dotenv import load_dotenv
import os

load_dotenv()
TG_TOKEN = os.getenv("TELEGRAM_TOKEN")
HOST = os.getenv("HOST")

db = DB()
bot = telebot.TeleBot(TG_TOKEN)
operator_messages = {}
connected_clients = {}
replied_messages = {}


def update_connected_clients():
    global connected_clients
    API_URL = f'{HOST}'
    response = requests.get(f"{API_URL}/clients")
    connected_clients = response.json()

@bot.callback_query_handler(func=lambda callback: True)
def handle_callback_query(callback):
    callback_data = callback.data.split('__')
    message = callback.message
    if len(callback_data) > 2:
        action = callback_data[1]
        payload = callback_data[2]
        chatId = callback_data[3] if len(callback_data)> 3 else None
        update_connected_clients()
        
        if action == "reply":
            msg = bot.send_message(callback.message.chat.id, "Your message:")
            bot.register_next_step_handler(msg, lambda message: process_reply(chatId, message, payload))
        elif action == "info":
            bot.send_message(message.chat.id, f"#{connected_clients[payload]}:\n")
        elif action == "setup":
            setup(message)
        elif action == "join":
            joinChatAsOperator(message)
        elif action == "add":
            add_operator(message)
        elif action == "operators":
            get_all_operators(message)
        elif action == "code":
            get_widget_code(message)
        elif action == 'operator':
            manage_operator(chatId, message, payload)
        elif action == 'remove':
            remove_operator(message, payload)
        elif action == 'edit':
            msg = bot.send_message(callback.message.chat.id, 'Enter new name:')
            bot.register_next_step_handler(msg, lambda message: edit_operator_name(message, payload, message.text))
        elif action == "menu":
            mainMenu(message)
        elif action == "back":
            if payload == "menu":
                mainMenu(message)
            elif payload == "operators":
                get_all_operators(message)
            else:
                mainMenu(message)

def process_reply(chatId, message, client_id):
    operator_name = db.getOperatorNameById(int(chatId), str(message.chat.id))
    result = send_message_to_client(client_id, {'text': message.text, 'sender': operator_name})
    
    if result:
        notify_operators_message_replied(chatId, client_id, operator_name)
    else:
        bot.send_message(message.chat.id, 'Client not connected')

@bot.message_handler(commands=['start'])
def start(message):
    toJoin = extract_unique_code(message.text)
    if toJoin:
        joinChatAsOperator(message, toJoin)
    else:
        user = db.chatsCollection.find_one({"_id": message.chat.id})
        if user:
            mainMenu(message)
        else:
            setup(message)

def setup(message):
    chat_id = message.chat.id
    username = message.chat.username
    name = message.from_user.first_name
    db.addAdmin(chat_id, username, name)
    db.addOperatorToChat(chat_id, username, chat_id, name)

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
    msg = bot.send_message(chat_id, "Enter first message that will appear in your chat:")
    bot.register_next_step_handler(msg, process_chat_message_step)

def process_chat_message_step(message):
    chat_id = message.chat.id
    chat_msg = message.text

    db.updateFirstMessage(chat_id, chat_msg)
    bot.send_message(chat_id, "Chat setup complete. Use Menu button to manage your chat.", reply_markup=nav.createKeyboardMenu())


def add_operator(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, f"Give this link to your operator:\nhttps://telegram.me/test28042501_bot?start={chat_id}", reply_markup=nav.createKeyboardMenu())

def joinChatAsOperator(message, toJoin):
    chatId = message.chat.id
    username = message.chat.username
    name = message.from_user.first_name

    db.addOperatorToChat(int(toJoin), username, chatId, name)
    bot.send_message(chatId, "You successfully joined as an operator.\nNow all incoming messages will directed to you.", reply_markup=nav.createKeyboardMenu())
    bot.send_message(toJoin, f'Operator @{username} successfully joined as an operator.', reply_markup=nav.createKeyboardMenu())

def get_all_operators(message):
    chat_id = message.chat.id
    chat_config = db.getChatConfig(chat_id)
    operators = chat_config['operators']

    result = 'Choose an operator:'
    return bot.send_message(chat_id, result, reply_markup=nav.createOperatorsMarkup(chat_id, operators))

def manage_operator(chatId, message, operatorId):
    chat = db.getChatConfig(int(chatId))
    operator = chat['operators'][operatorId]
    text = f"Operator:\n{operator['operator_name']} (@{operator['operator_username']})"
    bot.send_message(message.chat.id, text, reply_markup=nav.createManageOperatorMarkup(chatId, operatorId))

def remove_operator(message, operator):
    result = db.removeOperator(message.chat.id, operator)
    if result:
        bot.send_message(message.chat.id, f'Operator @{operator}, successfully removed', reply_markup=nav.createKeyboardMenu())
    else:
        bot.send_message(message.chat.id, f'Server error when removing operator @{operator}', reply_markup=nav.createKeyboardMenu())

def edit_operator_name(message, operator_id, newName):
    result = db.updateOperatorNameById(message.chat.id, operator_id, newName)
    if result:
        bot.send_message(message.chat.id, f'Operator renamed successfully', reply_markup=nav.createKeyboardMenu())
    else:
        bot.send_message(message.chat.id, f'Server error when editing operator {newName}', reply_markup=nav.createKeyboardMenu())

def get_widget_code(message):
    chat_id = message.chat.id
    chat_config = db.getChatConfig(chat_id)

    if chat_config:
        unique_code = chat_config['unique_code']
        widget_code = f"""
        <script>
        var userCode = '{unique_code}';
        (function() {{
            var script = document.createElement('script');
            script.src = "{HOST}/js/client.js";
            document.head.appendChild(script);
        }})();
        </script>
        """
        bot.send_message(chat_id, "Paste the following code into your website:")
        bot.send_message(chat_id, f"```html\n{widget_code}\n```", parse_mode='Markdown', reply_markup=nav.createKeyboardMenu())
    else:
        bot.send_message(chat_id, "Chat not set up. Please use /setup to set up the chat.", reply_markup=nav.createKeyboardMenu())


@bot.message_handler()
def message_handler(message):
    if (message.text == "Menu"):
        mainMenu(message)
    elif (message.text == "Help"):
        bot.send_message(message.chat.id, "If have any queries about the bot write @isnotbeka for further assistance.")
    else:
        bot.send_message(message.chat.id, "You need to select a client to reply first.")


def mainMenu(message):
    chat_id = message.chat.id
    chat = db.chatsCollection.find_one({"_id": chat_id})
    if chat:
        chatName = chat['chat_name']
        chatDescription = chat['description']
        chatGreeting = chat['greeting']
        chatAdminUsername = chat['admin']['username']
        chatAdminName = chat['admin']['name']

        text = [f"{chatName}\n",
        f"{chatDescription}\n",
        f"First message: {chatGreeting}\n",
        "Status: Online\n\n",
        f"You: {chatAdminName} (@{chatAdminUsername})\n",
        f"Role: Admin{", Operator" if str(chat_id) in chat['operators'] else ""}"]
        text = ''.join(text)
        
        bot.send_message(chat_id, text, reply_markup=nav.mainMenuMarkup)
    else:
        print("Chat not found")

def notify_operators_message_replied(chat_id, sender_id, operator_name):
    mock_name = connected_clients[sender_id]
    chat_config = db.getChatConfig(int(chat_id))
    
    if chat_config:
        operators = chat_config['operators'].keys()
        for operator_chat_id in operators:
            
            bot.send_message(operator_chat_id, f'Message from #{mock_name} has been replied to by {operator_name}.')
    else:
        print(f"Chat configuration not found for chat_id: {chat_id}")

def extract_unique_code(text):
    # Extracts the unique_code from the sent /start command.
    return text.split()[1] if len(text.split()) > 1 else None

def start_telegram_bot():
    bot.polling(none_stop=True)

if __name__ == '__main__':
    start_telegram_bot()