import socket
import threading
from cryptography.fernet import Fernet

# Generate and save a key for encryption
key = Fernet.generate_key()
cipher = Fernet(key)
print(f"Encryption Key (share with clients): {key.decode()}")

clients = {}

def broadcast(message, sender_socket=None):
    """Broadcast a message to all clients except the sender."""
    for client_socket in clients:
        if client_socket != sender_socket:
            client_socket.send(message)

def handle_client(client_socket, address):
    try:
        # Receive and decrypt the username
        encrypted_username = client_socket.recv(1024)
        username = cipher.decrypt(encrypted_username).decode()
        clients[client_socket] = username

        print(f"{username} has joined from {address}.")
        broadcast(cipher.encrypt(f"{username} has joined the chat.".encode()), sender_socket=None)

        while True:
            encrypted_message = client_socket.recv(1024)
            if not encrypted_message:
                break
            decrypted_message = cipher.decrypt(encrypted_message).decode()
            print(decrypted_message)
            broadcast(encrypted_message, sender_socket=client_socket)
    except Exception as e:
        print(f"Error with {address}: {e}")
    finally:
        username = clients.pop(client_socket, "Unknown user")
        broadcast(cipher.encrypt(f"{username} has left the chat.".encode()), sender_socket=None)
        client_socket.close()
        print(f"Connection closed: {address}")

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("0.0.0.0", 5000))
server.listen(5)
print("Server listening on port 5000...")

while True:
    client_socket, addr = server.accept()
    threading.Thread(target=handle_client, args=(client_socket, addr)).start()
