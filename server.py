import socket
import threading
import dh
import sys
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("chat_system.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

connections = {}
clients = {}
client_public_keys = {}

def handle_client(conn, addr, username):
    global server_public_key, server_private_key
    try:
        conn.sendall(str(server_public_key).encode())
        client_public_key = int(conn.recv(1024).decode())
        client_public_keys[username] = client_public_key
        clients[username] = conn
        connections[username] = conn

        while True:
            recipient_name = conn.recv(1024).decode()
            if not recipient_name:
                break

            if recipient_name in clients:
                recipient_conn = clients[recipient_name]
                recipient_public_key = client_public_keys[recipient_name]
                conn.sendall(str(recipient_public_key).encode())
                encrypted_message = conn.recv(1024)
                sender_public_key = client_public_keys[username]
                recipient_conn.sendall(f"{sender_public_key}\n".encode() + encrypted_message)
            else:
                conn.sendall(b"Recipient not found")
                logging.error(f"Recipient {recipient_name} not found")
    except Exception as e:
        logging.error(f"Error in handle_client for {username}: {e}")
    finally:
        conn.close()
        if username in clients:
            del clients[username]
        if username in client_public_keys:
            del client_public_keys[username]
        if username in connections:
            del connections[username]
        logging.info(f"Connection closed for {username}")

def start_server():
    global server_public_key, server_private_key
    server_private_key = dh.generate_private_key()
    server_public_key = dh.compute_public_key(server_private_key, dh.P, dh.G)

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('0.0.0.0', 9999))
    server_socket.listen()
    logging.info("Server listening on port 9999...")

    while True:
        try:
            conn, addr = server_socket.accept()
            logging.info(f"New connection from {addr}")

            conn.sendall(b'Please enter your username:')
            username = conn.recv(1024).decode()

            if username not in clients:
                conn.sendall(b'Username accepted.')
                logging.info(f"Client {username} connected from {addr}")
                threading.Thread(target=handle_client, args=(conn, addr, username), daemon=True).start()
            else:
                conn.sendall(b'Username already taken. Please choose another username.')
                conn.close()
        except Exception as e:
            logging.error(f"Error in start_server: {e}")
            sys.exit(1)

if __name__ == "__main__":
    start_server()
