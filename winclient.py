import socket
import dh
import sys
import threading
import logging

# Setup logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)  # Base level for the logger

# FileHandler for all INFO and above
file_handler = logging.FileHandler("chat_system.log")
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))

# StreamHandler for ERROR and above only
stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setLevel(logging.ERROR)  # Only ERROR and above will print to console
stream_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))

# Add handlers to the logger
logger.handlers = []  # Clear any default handlers
logger.addHandler(file_handler)
logger.addHandler(stream_handler)

def xor_encrypt_decrypt(key, message):
    return bytes([b ^ key for b in message])

def receive_messages(sock, username, private_key, condition, shared_state):
    """Thread function to handle incoming messages from the server."""
    while True:
        try:
            data = sock.recv(1024)
            if not data:
                logging.info("Server disconnected")
                print("\nServer disconnected.")
                break

            with condition:
                if shared_state["expecting_key"]:
                    if data == b"Recipient not found":
                        logging.error("Recipient not found. Try again.")
                        shared_state["expecting_key"] = False
                        shared_state["recipient_public_key"] = None
                        print("\nRecipient not found. Enter recipient username: ", end="", flush=True)
                        condition.notify()
                    else:
                        shared_state["recipient_public_key"] = int(data.decode())
                        shared_state["expecting_key"] = False
                        print("\nEnter message: ", end="", flush=True)
                        condition.notify()
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
                        logging.warning(f"Received unexpected data: {data!r}")
                        continue

        except Exception as e:
            logging.error(f"Error in receive_messages: {e}")
            break

    sock.close()

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
        if response.startswith('Username accepted.'):
            break
        logging.info("Username rejected by server. Try again.")
        print("Username rejected. Please try again.")

    # Extract server public key from the response if included
    if len(response) > len('Username accepted.'):
        server_public_key = int(response[len('Username accepted.'):])
    else:
        server_public_key = int(s.recv(1024).decode())

    # Generate and send client public key
    private_key = dh.generate_private_key()
    public_key = dh.compute_public_key(private_key, dh.P, dh.G)
    s.sendall(str(public_key).encode())

    # Shared state with synchronization
    condition = threading.Condition()
    shared_state = {
        "sending": False,
        "recipient": None,
        "recipient_public_key": None,
        "expecting_key": False
    }

    # Start the receiver thread
    recv_thread = threading.Thread(
        target=receive_messages,
        args=(s, username, private_key, condition, shared_state),
        daemon=True
    )
    recv_thread.start()

    print("Chat started. Enter a recipient username to send a message.")
    print("Enter recipient username: ", end="", flush=True)

    # Main thread handles user input
    while True:
        try:
            line = input("")  # Blocking input, but receiver thread runs independently
            with condition:
                if not shared_state["sending"]:
                    # First input is the recipient
                    shared_state["recipient"] = line.strip()
                    if not shared_state["recipient"]:
                        print("Enter recipient username: ", end="", flush=True)
                        continue
                    shared_state["expecting_key"] = True
                    s.sendall(shared_state["recipient"].encode())
                    shared_state["sending"] = True
                    shared_state["recipient_public_key"] = None
                    logging.info(f"Sent recipient username: {shared_state['recipient']}")
                    # Wait for receiver to get the public key or error
                    while shared_state["sending"] and shared_state["recipient_public_key"] is None and s.fileno() != -1:
                        condition.wait(timeout=5.0)
                    if shared_state["recipient_public_key"] is None:
                        shared_state["sending"] = False
                        continue
                elif shared_state["sending"] and shared_state["recipient_public_key"] is not None:
                    # Second input is the message
                    message = line.strip()
                    if not message:
                        print("Enter message: ", end="", flush=True)
                        continue
                    full_message = f"{username}: {message}".encode()
                    shared_secret = dh.compute_shared_secret(private_key, shared_state["recipient_public_key"], dh.P)
                    shared_key = shared_secret % 256
                    encrypted_message = xor_encrypt_decrypt(shared_key, full_message)
                    s.sendall(encrypted_message)
                    logging.info(f"Sent encrypted message to {shared_state['recipient']}")
                    shared_state["sending"] = False
                    shared_state["recipient"] = None
                    shared_state["recipient_public_key"] = None
                    print("Enter recipient username: ", end="", flush=True)
        except EOFError:
            logging.info("User terminated input (Ctrl+D/Ctrl+Z)")
            break
        except Exception as e:
            logging.error(f"Error in main thread: {e}")
            break

    s.close()

if __name__ == "__main__":
    start_client()