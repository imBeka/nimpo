from flask import Flask, request, redirect, jsonify, send_from_directory
from flask_socketio import emit, SocketIO
from db import DB
from flask_cors import CORS
# from bot import send_message_to_operators, send_file_to_telegram
from shared import register_client, unregister_client
import os
import tempfile
import requests
import json
import hashlib

# Define your bot token here
BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")

# Define the base URL for the Telegram Bot API
BASE_URL = f'https://api.telegram.org/bot{BOT_TOKEN}/'

socketio = SocketIO()
db = DB()
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'
cors = CORS(app)
socketio.init_app(app, cors_allowed_origins="*")

def send_message_to_operators(chat_id, message, sender_id, chat_name):
    mock_name = connected_clients[sender_id]

    # Create inline keyboard markup with buttons
    reply_markup = {
        "inline_keyboard": [
            [
                {"text": "reply", "callback_data": f"__reply__{sender_id}__{chat_id}"}
            ]
        ]
    }

    # Convert reply_markup to JSON
    reply_markup_json = json.dumps(reply_markup)

    chat_config = db.getChatConfig(chat_id)
    
    if chat_config:
        operators = chat_config['operators'].keys()
        for operator_chat_id in operators:
            # Prepare the data for the message
            data = {
                'chat_id': operator_chat_id,
                'text': f'#{mock_name} from - {chat_name}\n\n{message}',
                'reply_markup': reply_markup_json
            }

            # Send the message via the Telegram Bot API
            response = requests.post(BASE_URL + 'sendMessage', data=data)

            # Check for any errors
            if response.status_code != 200:
                print(f"Failed to send message to operator {operator_chat_id}: {response.text}")
            else:
                print(f"Message sent to operator {operator_chat_id}")
    else:
        print(f"Chat configuration not found for chat_id: {chat_id}")

connected_clients = {}

@app.route('/clients', methods=['GET'])
def get_connected_clients():
    return jsonify(connected_clients)

@app.route('/clients/<client_id>', methods=['POST'])
def register_client(client_id):
    if client_id not in connected_clients:
        mock_name = generate_funny_name(client_id)
        connected_clients[client_id] = mock_name
        print(f"Client {client_id} registered as {mock_name}")
        return jsonify({'status': 'registered', 'name': mock_name}), 201
    else:
        return jsonify({'status': 'already_registered'}), 200

@app.route('/clients/<client_id>', methods=['DELETE'])
def unregister_client(client_id):
    if client_id in connected_clients:
        del connected_clients[client_id]
        print(f"Client {client_id} unregistered")
        return jsonify({'status': 'unregistered'}), 200
    else:
        return jsonify({'status': 'not_found'}), 404

@app.route('/clients/<client_id>/message', methods=['POST'])
def send_message_to_client(client_id):
    data = request.json
    message = data.get('message')
    if client_id in connected_clients:
        socketio.emit('message', message, room=client_id)
        print(f"Message sent to client {connected_clients[client_id]} ({client_id}): {message}")
        return jsonify({'status': 'message_sent'}), 200
    else:
        print(f"Client {client_id} not connected")
        return jsonify({'status': 'client_not_connected'}), 404


# API server for client.js
@app.route('/get_chat_config', methods=['GET'])
def get_chat_config():
    user_code = request.args.get('user_code')

    chat = db.getChatByCode(user_code)
    user = db.getUserByCode(user_code)
    if chat:
        return jsonify({
            'id': chat.get('_id', "Default Chat Id"),
            'chatName': chat.get('chat_name', 'Default Chat Name'),
            'description': chat.get('description', 'Default Description'),
            'greeting': chat.get('greeting', 'Default Greeting'),
            'plan': 'Trial'  # Replace with actual subscription check
        })
    
    return jsonify({'error': 'Chat config not found'}), 404

@app.route('/upload', methods=['POST'])
def upload_file():
    sender_id = 0
    chat_id = request.form['chat_id']
    chat_name = request.form['chat_name']
    file = request.files['file']

    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)
    if file and file.content_type.startswith('image/'):
        send_file_to_telegram(chat_id, file, sender_id, chat_name)
        return 'Image successfully uploaded and sent to Telegram.'
    else:
        return 'Invalid file type. Please upload an image.'

@app.after_request
def after_request(response):
    response.headers.set('Access-Control-Allow-Origin', '*')
    response.headers.set('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.set('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response 

@app.route('/')
def render():
    return '<h1>Hello World!</h1>'

@app.route('/img/<path:filename>')
def img(filename):
    return send_from_directory('static/img', filename)

@app.route('/fonts/<path:filename>')
def fonts(filename):
    return send_from_directory('static/fonts', filename)

@app.route('/js/<path:filename>')
def script(filename):
    return send_from_directory('static/js', filename)

@app.route('/styles/<path:filename>')
def css(filename):
    return send_from_directory('static/css', filename)

@socketio.on('connect')
def handle_connect():
    client_address = request.remote_addr
    remote_user = request.remote_user
    print(client_address)
    client_id = request.sid
    register_client(client_id)
    emit('client_registered', {'client_id': client_id, 'client_address': client_address, 'remote_user': remote_user})

@socketio.on('disconnect')
def handle_disconnect():
    client_id = request.sid
    unregister_client(client_id)

@socketio.on('message')
def handle_message(data):
    sender_id = request.sid
    chat_id = data['chatId']
    chat_name = data['chatName']

    if data['type'] == 'attachment':
        # Save the received file
        temp_dir = tempfile.gettempdir()
        file_path = os.path.join(temp_dir, data['filename'])
        with open(file_path, 'wb') as f:
            f.write(data['data'])

        # Send the file to the Telegram bot
        with open(file_path, 'rb') as f:
            send_file_to_telegram(chat_id, f, sender_id, chat_name)
        os.remove(file_path)

    else:
        message = data['text']
        send_message_to_operators(chat_id, message, sender_id, chat_name)


def generate_funny_name(input_string):
    # Calculate a consistent hash value for the input string
    hash_value = hashlib.md5(input_string.encode()).hexdigest()

    # Define a list of adjectives and nouns for generating funny names
    adjectives = ['massive', 'colorful', 'happy', 'cheerful', 'silly', 'jolly', 'playful', 'quirky', 'whimsical', 'zany']
    nouns = ['unicorn', 'penguin', 'cormorant', 'giraffe', 'platypus', 'narwhal', 'koala', 'sloth', 'octopus', 'toucan']

    # Use the hash value to select an adjective and noun from the lists
    adjective_index = int(hash_value, 16) % len(adjectives)
    noun_index = int(hash_value, 16) % len(nouns)

    # Construct the funny name using the selected adjective and noun
    funny_name = adjectives[adjective_index] + '_' + nouns[noun_index]

    return funny_name

def start_flask_server():
    socketio.run(app, host='0.0.0.0', port=8000, debug=True, use_reloader=False)
    app.run()

if __name__ == '__main__':
    app.run() 