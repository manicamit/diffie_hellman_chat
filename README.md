# 🔐 Secure Chat System with Diffie-Hellman

## Overview
This is a secure chat implementation in Python using the Diffie-Hellman key exchange protocol for end-to-end encryption between clients.

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
The server will start listening on port 9999.

### Running a Client
```bash
python client.py
```
Follow the prompts to:
1. Enter your username
2. Enter recipient's username
3. Start sending messages

## Security Features
- Implementation of Diffie-Hellman key exchange protocol
- Unique session keys for each client pair
- XOR encryption for message content
- No storage of encryption keys

## ⚠️ Security Disclaimer
This implementation is for educational purposes. While it demonstrates the principles of secure communication, it may not be suitable for production use without additional security measures.

## License
This project is open source and available under the MIT License.

