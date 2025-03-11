import socket
import dh
import select
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

def xor_encrypt_decrypt(key, message):
    return bytes([b ^ key for b in message])

def start_client():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect(('localhost', 9999))
        logging.info("Connected to server on localhost:9999")
    except Exception as e:
        logging.error(f"Failed to connect to server: {e}")
        sys.exit(1)

    # Username setup
    while True:
        response = s.recv(1024).decode()
        print(response)
        username = input("Enter your username: ")
        s.sendall(username.encode())
        response = s.recv(1024).decode()
        print(response)
        if response == 'Username accepted.':
            break
        logging.error("Username rejected. Try again.")

    # Key exchange
    server_public_key = int(s.recv(1024).decode())
    private_key = dh.generate_private_key()
    public_key = dh.compute_public_key(private_key, dh.P, dh.G)
    s.sendall(str(public_key).encode())

    # State variables
    sending = False
    expecting_key = False
    recipient = None
    recipient_public_key = None

    print("Chat started. Enter a recipient username to send a message.")
    print("Enter recipient username: ", end="", flush=True)

    while True:
        readable, _, _ = select.select([s, sys.stdin], [], [], 0.1)

        # Handle incoming messages from server
        if s in readable:
            data = s.recv(1024)
            if not data:
                logging.info("Server disconnected")
                break

            if expecting_key:
                if data == b"Recipient not found":
                    logging.error("Recipient not found. Try again.")
                    sending = False
                    expecting_key = False
                    print("Enter recipient username: ", end="", flush=True)
                else:
                    recipient_public_key = int(data.decode())
                    expecting_key = False
                    print("Enter message: ", end="", flush=True)
            else:
                # Incoming message
                try:
                    sender_public_key, encrypted_data = data.split(b'\n', 1)
                    sender_public_key = int(sender_public_key.decode())
                    shared_secret = dh.compute_shared_secret(private_key, sender_public_key, dh.P)
                    shared_key = shared_secret % 256
                    decrypted_message = xor_encrypt_decrypt(shared_key, encrypted_data).decode()
                    if not decrypted_message.startswith(f"{username}:"):
                        print(f"\n[MSG] {decrypted_message}")
                    print("Enter recipient username: ", end="", flush=True)
                except ValueError:
                    continue

        # Handle user input
        if sys.stdin in readable:
            line = sys.stdin.readline().strip()
            if not sending:
                # First input is the recipient
                recipient = line
                s.sendall(recipient.encode())
                expecting_key = True
                sending = True
            elif sending and not expecting_key:
                # Second input is the message
                message = line
                full_message = f"{username}: {message}".encode()
                shared_secret = dh.compute_shared_secret(private_key, recipient_public_key, dh.P)
                shared_key = shared_secret % 256
                encrypted_message = xor_encrypt_decrypt(shared_key, full_message)
                s.sendall(encrypted_message)
                sending = False
                recipient = None
                recipient_public_key = None
                print("Enter recipient username: ", end="", flush=True)

    s.close()

if __name__ == "__main__":
    start_client()
