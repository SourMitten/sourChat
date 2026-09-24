# Python LAN Chat

A simple terminal-based TCP chat application written in Python.

It supports a **host/server mode** and a **client mode**, username authentication, optional password protection, timestamps, logging, and desktop notifications.

## Features

- TCP-based client/server chat
- Multiple simultaneous clients
- Username support
- Optional password authentication
- Host and client modes
- Timestamped messages
- Join/leave system messages
- Chat logging to `chat.log`
- Desktop notifications
- `/quit` command
- Command-line arguments using `argparse`
- JSON-based communication protocol

## Requirements

- Python 3.x
- Network connection between the host and clients
- `win11toast`

Install the required Python package:

```bash
pip install win11toast
```

### Linux Notifications

Linux users may also need `notify-send`.

On Debian/Ubuntu:

```bash
sudo apt install libnotify-bin
```

## Usage

The basic syntax is:

```bash
python chat.py --dev <host|client> --port <PORT> --username <USERNAME> [OPTIONS]
```

## Arguments

| Argument | Required | Description |
|---|---|---|
| `--dev` | Yes | Selects the operating mode: `host` or `client` |
| `--port` | Yes | TCP port used by the host/client |
| `--username` | Yes | Username displayed in chat |
| `--target` | Client only | IP address or hostname of the host |
| `--password` | No | Optional password for connecting to the host |

---

## `--dev`

Selects whether the program runs as a host or client.

### Host

```bash
--dev host
```

The host creates the chat server and waits for clients to connect.

### Client

```bash
--dev client
```

The client connects to an existing host.

Only these values are accepted:

```text
host
client
```

---

## `--port`

Specifies the TCP port used by the application.

The host listens on this port:

```bash
python chat.py --dev host --port 5000 --username Alice
```

Clients must use the same port:

```bash
python chat.py --dev client --target 192.168.1.100 --port 5000 --username Bob
```

The port can be any available TCP port, assuming it is allowed by the firewall.

---

## `--username`

Specifies the username displayed in chat.

Example:

```bash
--username Alice
```

Messages will appear like:

```text
[12:30:45] Alice: Hello!
```

The username is required in both host and client mode.

---

## `--target`

Specifies the IP address or hostname of the host.

This argument is required when using client mode.

Example:

```bash
--target 192.168.1.100
```

For a host running on the same computer, you can use:

```bash
--target 127.0.0.1
```

Example:

```bash
python chat.py --dev client --target 127.0.0.1 --port 5000 --username Bob
```

---

## `--password`

Sets an optional password for the host.

### Host

```bash
python chat.py --dev host --port 5000 --username Alice --password secret123
```

### Client

The client must provide the same password:

```bash
python chat.py --dev client --target 192.168.1.100 --port 5000 --username Bob --password secret123
```

If the host does not specify a password, clients can connect without one.

If a password is configured and the client provides the wrong password, the connection is rejected.

---

# Quick Start

## 1. Start the Host

On the computer that will host the chat:

```bash
python chat.py --dev host --port 5000 --username Alice
```

The host will display something similar to:

```text
[12:30:00] Host 'Alice' listening on port 5000
```

## 2. Find the Host's IP Address

On Windows:

```powershell
ipconfig
```

Look for the host's local IPv4 address, for example:

```text
IPv4 Address. . . . . . . . . . . : 192.168.1.100
```

## 3. Connect a Client

On another computer on the same network:

```bash
python chat.py --dev client --target 192.168.1.100 --port 5000 --username Bob
```

The client should display:

```text
Connected as Bob. Type /quit to exit.
>
```

## 4. Start More Clients

Additional clients can connect using the same host IP and port:

```bash
python chat.py --dev client --target 192.168.1.100 --port 5000 --username Charlie
```

```bash
python chat.py --dev client --target 192.168.1.100 --port 5000 --username Dave
```

All connected clients can communicate through the host.

---

# Example

Suppose the host is:

```text
192.168.1.100
```

The host runs:

```bash
python chat.py --dev host --port 5000 --username Alice
```

Bob connects with:

```bash
python chat.py --dev client --target 192.168.1.100 --port 5000 --username Bob
```

Charlie connects with:

```bash
python chat.py --dev client --target 192.168.1.100 --port 5000 --username Charlie
```

If Bob sends:

```text
Hello everyone!
```

The other clients receive:

```text
[12:35:21] Bob: Hello everyone!
```

---

# Password-Protected Example

Start the host with:

```bash
python chat.py --dev host --port 5000 --username Alice --password mypassword
```

Clients must provide the same password:

```bash
python chat.py --dev client --target 192.168.1.100 --port 5000 --username Bob --password mypassword
```

A client using the wrong password will be rejected.

---

# Leaving the Chat

Clients can leave the chat by typing:

```text
/quit
```

Example:

```text
> /quit
Disconnected.
```

The server will broadcast a system message:

```text
[12:36:00] *** Bob left ***
```

---

# System Messages

The server automatically generates messages when clients join or leave.

Example:

```text
[12:30:00] *** Bob joined ***
[12:31:15] *** Charlie joined ***
[12:35:00] *** Bob left ***
```

---

# Logging

The host writes chat activity to:

```text
chat.log
```

Example:

```text
2026-09-24 12:30:00,123 [12:30:00] *** Bob joined ***
2026-09-24 12:30:15,456 [12:30:15] Bob: Hello!
2026-09-24 12:31:00,789 [12:31:00] *** Bob left ***
```

The log file is created in the program's current working directory.

---

# Notifications

Clients attempt to display a desktop notification whenever a new chat message is received.

## Windows

The application uses:

```python
win11toast
```

Install it with:

```bash
pip install win11toast
```

## Linux

The application attempts to use:

```bash
notify-send
```

On Debian/Ubuntu:

```bash
sudo apt install libnotify-bin
```

If notifications are unavailable, the chat itself will continue to function.

---

# Network Configuration

The host listens on:

```text
0.0.0.0:<port>
```

For example:

```bash
python chat.py --dev host --port 5000 --username Alice
```

This allows clients to connect through the host's network interfaces.

A client on the same LAN could connect using:

```bash
python chat.py --dev client --target 192.168.1.100 --port 5000 --username Bob
```

## Firewall

If clients cannot connect, make sure the host's firewall allows inbound TCP connections on the selected port.

For example, if using port `5000`, allow TCP traffic on port `5000`.

---

# Communication Protocol

The application communicates using newline-delimited JSON messages over TCP.

## Authentication

When a client connects, it sends:

```json
{
    "type": "auth",
    "username": "Bob",
    "password": "secret"
}
```

The server validates the username and password.

---

## Chat Message

A client sends:

```json
{
    "type": "msg",
    "msg": "Hello!"
}
```

The server adds the username and timestamp before broadcasting the message.

---

## Exit

When a client uses `/quit`, it sends:

```json
{
    "type": "exit"
}
```

The server removes the client from the connected-client list and broadcasts a leave message.

---

# Architecture

The application has two primary modes.

## Host

The host:

1. Creates a TCP socket.
2. Binds to `0.0.0.0` and the selected port.
3. Listens for incoming connections.
4. Receives authentication information.
5. Validates the username and optional password.
6. Adds authenticated clients to the client list.
7. Creates a thread for each client.
8. Receives messages from clients.
9. Broadcasts messages to other clients.
10. Handles client disconnects.

## Client

The client:

1. Connects to the host.
2. Sends authentication information.
3. Starts a receiving thread.
4. Reads user input from the terminal.
5. Sends messages to the host.
6. Displays messages received from the host.
7. Displays desktop notifications.
8. Sends an exit message when `/quit` is used.

---

# Command Reference

## Host

Basic host:

```bash
python chat.py --dev host --port PORT --username USERNAME
```

Host with password:

```bash
python chat.py --dev host --port PORT --username USERNAME --password PASSWORD
```

Example:

```bash
python chat.py --dev host --port 5000 --username Alice --password secret123
```

## Client

Basic client:

```bash
python chat.py --dev client --target HOST_IP --port PORT --username USERNAME
```

Client with password:

```bash
python chat.py --dev client --target HOST_IP --port PORT --username USERNAME --password PASSWORD
```

Example:

```bash
python chat.py --dev client --target 192.168.1.100 --port 5000 --username Bob --password secret123
```

---

# Troubleshooting

## Connection Failed

If you see:

```text
Connection failed: ...
```

Check that:

- The host is running.
- The host IP address is correct.
- The client is using the correct port.
- Both devices can communicate over the network.
- The host firewall allows the selected port.
- The host is listening on the expected port.

---

## `Client mode requires --target`

You started the program in client mode without specifying the host.

Use:

```bash
python chat.py --dev client --target 192.168.1.100 --port 5000 --username Bob
```

---

## `ERROR: --port is required`

Specify a port:

```bash
--port 5000
```

Example:

```bash
python chat.py --dev host --port 5000 --username Alice
```

---

## `ERROR: --username is required`

Specify a username:

```bash
--username Alice
```

Example:

```bash
python chat.py --dev host --port 5000 --username Alice
```

---

## Authentication Failed

If the server requires a password, make sure the client uses the same password:

```bash
--password mypassword
```

The password must match exactly.

---

## Notifications Do Not Appear

On Windows, install:

```bash
pip install win11toast
```

On Linux, make sure `notify-send` is installed:

```bash
sudo apt install libnotify-bin
```

---

# Security

This project is intended as a simple chat application and **is not a secure production messaging system**.

Important security considerations:

- TCP traffic is not encrypted.
- Passwords are transmitted directly over the TCP connection.
- Passwords are not hashed.
- There is no TLS/SSL.
- There is no persistent user/account system.
- There is no rate limiting.
- There is no message encryption.
- The host listens on all network interfaces.
- There is no protection against malicious clients.
- Broad exception handling is used in several places.

**Do not use this implementation to transmit sensitive or confidential information over an untrusted network.**

For a more secure implementation, consider adding TLS/SSL to the socket connection and using a proper password-hashing system.

---

# Current Limitations

- The host runs continuously until the process is terminated.
- There is no graphical user interface.
- There is no chat history synchronization for newly connected clients.
- There is no private/direct messaging.
- There are no administrator commands.
- There is no persistent account system.
- There is no encryption.
- Terminal input behavior may vary between operating systems and terminals.
- The server uses a connection backlog of `10`.
- The JSON protocol is newline-delimited.
- The application is intended primarily for simple LAN-based communication.

---

# Project Structure

A minimal project can look like:

```text
project/
├── chat.py
├── chat.log
└── README.md
```

`chat.log` is generated automatically when the program runs.

---

# Example Session

### Host

```bash
python chat.py --dev host --port 5000 --username Alice
```

Output:

```text
[12:30:00] Host 'Alice' listening on port 5000
[12:30:15] *** Bob joined ***
[12:30:30] Bob: Hello!
[12:31:00] *** Charlie joined ***
```

### Bob

```bash
python chat.py --dev client --target 192.168.1.100 --port 5000 --username Bob
```

Output:

```text
Connected as Bob. Type /quit to exit.
> Hello!
```

### Charlie

```bash
python chat.py --dev client --target 192.168.1.100 --port 5000 --username Charlie
```

Output:

```text
Connected as Charlie. Type /quit to exit.
[12:30:30] Bob: Hello!
>
```

---

# License

Add your project's license here.

For example:

```text
MIT License
```

If this project is not open source, replace this section with the appropriate licensing information.
