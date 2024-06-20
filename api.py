from flask import Flask, request, redirect, jsonify, send_from_directory
from flask_socketio import emit
from db import DB
from flask_cors import CORS
from bot import send_message_to_operators, send_file_to_telegram
from shared import socketio, register_client, unregister_client
import os
import tempfile


db = DB()
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'
cors = CORS(app)
socketio.init_app(app, cors_allowed_origins="*")

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


def start_flask_server():
    socketio.run(app, host='0.0.0.0', port=8080, debug=True, use_reloader=False)

if __name__ == '__main__':
    start_flask_server()