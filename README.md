# 🔐 Secure Chat System with Diffie-Hellman

## Overview
This is a secure chat implementation in Python using the Diffie-Hellman key exchange protocol for end-to-end encryption between clients.

## ⚠️ Compatibility
🐧 **Linux Only**: This application currently works only on Linux systems. Cross-platform support will be added in future updates.

**Update: winclient was added for cross platform connections, you can use winclient entirely for Linux to Linux or cross platform , while the client.py supports only Linux to Linux chats**

## Features
- 🔒 End-to-end encryption using Diffie-Hellman key exchange
- 👥 Multiple client support
- 🌐 Client-to-client secure messaging
- ⚡ Real-time message delivery
- 🛡️ Protection against man-in-the-middle attacks
 
## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/diffie-hellman-chat.git
   cd diffie-hellman-chat
   ```

## Usage
### Starting the Server
```bash
python server.py
```
The server will start listening on port 9999. You should see output similar to:
```
[INFO] Server started on 0.0.0.0:9999
[INFO] Waiting for connections...
```

### Running a Client
```bash
python client.py
```

### Detailed Usage Steps
1. **Start the server** on a machine (can be the same machine for testing)
2. **Launch client instances** on one or more machines:
   ```bash
   python client.py
   ```
3. **Register a username** when prompted:
   ```
   Enter your username: Alice
   [INFO] Connected to server
   [INFO] Registered as: Alice
   ```
4. **Select a recipient** to start a chat:
   ```
   Enter recipient username: Bob
   [INFO] Initiating secure connection with Bob...
   [INFO] Diffie-Hellman key exchange completed
   [INFO] Secure channel established with Bob
   ```
5. **Start messaging**:
   ```
   You: Hello Bob, this message is encrypted!
   Bob: Hi Alice, I can only see this because we have a secure channel!
   ```
6. **End a conversation** by typing `/quit` or press Ctrl+C to exit completely

### Example Chat Session
```
Alice (typing): Hello Bob, this is a secure message
[INFO] Message encrypted and sent to Bob

Bob (receives): Hello Bob, this is a secure message
[INFO] Message decrypted from Alice

Bob (typing): Hey Alice, I received your secure message
[INFO] Message encrypted and sent to Alice

Alice (receives): Hey Alice, I received your secure message
[INFO] Message decrypted from Bob
```
## Security Features
- Implementation of Diffie-Hellman key exchange protocol
- Unique session keys for each client pair
- XOR encryption for message content
- No storage of encryption keys

## ⚠️ Security Disclaimer
This implementation is for educational purposes. While it demonstrates the principles of secure communication, it may not be suitable for production use without additional security measures.

## License
This project is open source and available under the MIT License.

