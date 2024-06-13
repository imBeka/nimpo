from flask_socketio import SocketIO
import hashlib

# Create a global SocketIO instance
socketio = SocketIO()

# Dictionary to keep track of connected clients
connected_clients = {}

# Function to register a new client
def register_client(client_id):
    mock_name = generate_funny_name(client_id)
    connected_clients[client_id] = mock_name
    print(f"Client {client_id} registered as {mock_name}")

# Function to unregister a client
def unregister_client(client_id):
    if client_id in connected_clients:
        del connected_clients[client_id]
        print(f"Client {client_id} unregistered")

# Function to send a message to a specific client
def send_message_to_client(client_id, message):
    if client_id in connected_clients:
        socketio.emit('message', message, room=client_id)
        print(f"Message sent to client {connected_clients[client_id]} ({client_id}): {message}")
        return True
    else:
        print(f"Client {client_id} not connected")
        return False

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