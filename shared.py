import requests

API_URL = 'https://nimpo-deploy-5933d9b45d32.herokuapp.com'  # Change this to your actual API URL

def register_client(client_id):
    response = requests.post(f'{API_URL}/clients/{client_id}')
    if response.status_code == 201:
        print(response.json())
    elif response.status_code == 200:
        print(f"Client {client_id} is already registered.")
    else:
        print(f"Failed to register client {client_id}")

def unregister_client(client_id):
    response = requests.delete(f'{API_URL}/clients/{client_id}')
    if response.status_code == 200:
        print(f"Client {client_id} unregistered successfully.")
    elif response.status_code == 404:
        print(f"Client {client_id} not found.")
    else:
        print(f"Failed to unregister client {client_id}")

def send_message_to_client(client_id, message):
    data = {'message': message}
    response = requests.post(f'{API_URL}/clients/{client_id}/message', json=data)
    if response.status_code == 200:
        print(f"Message sent to client {client_id}: {message}")
    elif response.status_code == 404:
        print(f"Client {client_id} not connected.")
    else:
        print(f"Failed to send message to client {client_id}")