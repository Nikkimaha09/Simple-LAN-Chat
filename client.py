import socket
import threading
from cryptography.fernet import Fernet

# Input the key shared by the server
key = input("Enter the encryption key: ").encode()
cipher = Fernet(key)

def receive_messages(sock):
    try:
        while True:
            encrypted_message = sock.recv(1024)
            if not encrypted_message:
                break
            print(cipher.decrypt(encrypted_message).decode())
    except Exception as e:
        print(f"Error receiving messages: {e}")
    finally:
        print("Disconnected from server.")
        sock.close()

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_ip = input("Enter server IP: ")
client.connect((server_ip, 5000))

# Send the username to the server
username = input("Enter your username: ")
encrypted_username = cipher.encrypt(username.encode())
client.send(encrypted_username)

# Start the thread to receive messages
thread = threading.Thread(target=receive_messages, args=(client,))
thread.daemon = True
thread.start()

try:
    while True:
        message = input()
        if message.lower() == "exit":
            break
        formatted_message = f"{username}: {message}"
        encrypted_message = cipher.encrypt(formatted_message.encode())
        client.send(encrypted_message)
except Exception as e:
    print(f"Error: {e}")
finally:
    client.close()
    print("Connection closed.")
