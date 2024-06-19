from flask import Flask, render_template, url_for, request, redirect, jsonify, send_from_directory
from flask_socketio import SocketIO, emit, join_room, leave_room, send, join_room, leave_room
from db import DB
from flask_cors import CORS
import json
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
    return render_template('index.html')  

@app.route('/demo.html')
def demo():
    return render_template('demo.html')  

@app.route('/img/<path:filename>')
def img(filename):
    return send_from_directory('static/img', filename)

@app.route('/fonts/<path:filename>')
def fonts(filename):
    return send_from_directory('static/fonts', filename)

# @app.route("/client.js")
# def client_js():
#     return render_template('client.js')

@app.route('/js/<path:filename>')
def script(filename):
    return send_from_directory('static/js', filename)

# @app.route("/script.js")
# def script():
#     return render_template('script.js')

@app.route('/styles/<path:filename>')
def css(filename):
    return send_from_directory('static/css', filename)

# @app.route("/styles.css")
# def css():
#     return render_template('styles.css')


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

    # Simulate the bot's reply
    # response_message = f"Reply to {sender_id}: {message}, I dont give a fuck"
    # In a real implementation, you would use requests to send this message to the bot and get a response

    # Send the response back to the client
    # emit('message', {'text': response_message, 'sender': 'operator'}, room=sender_id)


def start_flask_server():
    socketio.run(app, debug=True, use_reloader=False, port=3000)

if __name__ == '__main__':
    start_flask_server()