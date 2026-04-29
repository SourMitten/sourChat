#!/usr/bin/env python3

import socket
import threading
import argparse
import json
import logging
import subprocess
from datetime import datetime
import os
import sys

clients = []
lock = threading.Lock()

# ---------- Client Input State ----------
current_input = ""
input_lock = threading.Lock()
running = True

# ---------- Utilities ----------

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def timestamp():
    return datetime.now().strftime("%H:%M:%S")

def format_sys(msg):
    return f"[{timestamp()}] *** {msg} ***"

def send_json(sock, data):
    try:
        sock.sendall((json.dumps(data) + "\n").encode())
    except:
        pass

def recv_json(sock):
    buffer = ""
    while True:
        chunk = sock.recv(1024).decode()
        if not chunk:
            return None
        buffer += chunk
        if "\n" in buffer:
            line, buffer = buffer.split("\n", 1)
            return json.loads(line)

def notify(title, message):
    try:
        subprocess.Popen(["notify-send", title, message])
    except:
        pass

# ---------- Host ----------

def broadcast(message, sender=None):
    with lock:
        for client in clients:
            if client != sender:
                send_json(client["sock"], message)

def handle_client(client):
    sock = client["sock"]
    username = client["username"]

    join_msg = format_sys(f"{username} joined")
    logging.info(join_msg)
    print(join_msg)

    broadcast({"type": "sys", "msg": join_msg})

    try:
        while True:
            data = recv_json(sock)
            if not data:
                break

            if data["type"] == "msg":
                msg = f"[{timestamp()}] {username}: {data['msg']}"
                logging.info(msg)
                print(msg)
                broadcast({"type": "msg", "msg": msg}, sender=client)

            elif data["type"] == "exit":
                break

    except:
        pass
    finally:
        with lock:
            if client in clients:
                clients.remove(client)

        leave_msg = format_sys(f"{username} left")
        logging.info(leave_msg)
        print(leave_msg)
        broadcast({"type": "sys", "msg": leave_msg})

        sock.close()

def run_host(port, password, username):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("0.0.0.0", port))
    server.listen(10)

    print(f"[{timestamp()}] Host '{username}' listening on port {port}")

    while True:
        sock, addr = server.accept()

        try:
            auth = recv_json(sock)
            if not auth or auth.get("type") != "auth":
                sock.close()
                continue

            client_username = auth.get("username", "").strip()
            client_pass = auth.get("password")

            if not client_username:
                send_json(sock, {"type": "sys", "msg": "Invalid username"})
                sock.close()
                continue

            if password and client_pass != password:
                send_json(sock, {"type": "sys", "msg": "Auth failed"})
                sock.close()
                continue

            client = {"sock": sock, "username": client_username}

            with lock:
                clients.append(client)

            threading.Thread(target=handle_client, args=(client,), daemon=True).start()

        except:
            sock.close()

# ---------- Client ----------

def receive_loop(sock):
    global current_input, running

    try:
        while running:
            data = recv_json(sock)
            if not data:
                break

            msg = data.get("msg", "")

            with input_lock:
                sys.stdout.write("\r" + " " * 100 + "\r")
                print(msg)
                sys.stdout.write("> " + current_input)
                sys.stdout.flush()

            if data["type"] == "msg":
                notify("New Message", msg)

    except:
        pass
    finally:
        running = False
        with input_lock:
            print("\nDisconnected from server.")

def run_client(target, port, username, password):
    global current_input, running

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        sock.connect((target, port))
    except Exception as e:
        print(f"Connection failed: {e}")
        return

    send_json(sock, {
        "type": "auth",
        "username": username,
        "password": password
    })

    threading.Thread(target=receive_loop, args=(sock,), daemon=True).start()

    print(f"Connected as {username}. Type /quit to exit.")

    sys.stdout.write("> ")
    sys.stdout.flush()

    while running:
        try:
            char = sys.stdin.read(1)
        except KeyboardInterrupt:
            break

        with input_lock:
            if char == "\n":
                msg = current_input.strip()
                print()

                if msg == "/quit":
                    running = False

                    # tell server we're leaving
                    send_json(sock, {"type": "exit"})

                    try:
                        sock.shutdown(socket.SHUT_RDWR)
                    except:
                        pass

                    break

                send_json(sock, {
                    "type": "msg",
                    "msg": msg
                })

                current_input = ""
                sys.stdout.write("> ")
                sys.stdout.flush()

            elif char in ("\x7f", "\x08"):  # backspace (handles more terminals)
                current_input = current_input[:-1]
                sys.stdout.write("\r> " + current_input + " ")
                sys.stdout.write("\r> " + current_input)
                sys.stdout.flush()

            else:
                current_input += char
                sys.stdout.write(char)
                sys.stdout.flush()

    sock.close()
    print("Disconnected.")

# ---------- Main ----------

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("--dev", required=True, choices=["host", "client"])
    parser.add_argument("--target", help="Host IP (client mode)")
    parser.add_argument("--port", type=int, help="Port (REQUIRED)")
    parser.add_argument("--username", help="Username (REQUIRED)")
    parser.add_argument("--password", default=None)

    args = parser.parse_args()

    clear()

    if not args.port:
        print("ERROR: --port is required")
        return

    if not args.username:
        print("ERROR: --username is required")
        return

    logging.basicConfig(
        filename="chat.log",
        level=logging.INFO,
        format="%(asctime)s %(message)s"
    )

    if args.dev == "host":
        run_host(args.port, args.password, args.username.strip())

    elif args.dev == "client":
        if not args.target:
            print("Client mode requires --target")
            return

        run_client(args.target, args.port, args.username.strip(), args.password)

if __name__ == "__main__":
    main()
