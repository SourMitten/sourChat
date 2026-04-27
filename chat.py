#!/usr/bin/env python3

import socket
import threading
import argparse
import json
import logging
import subprocess
from datetime import datetime

clients = []
lock = threading.Lock()

# ---------- Utilities ----------

def timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

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

# ---------- Host Logic ----------

def broadcast(message, sender=None):
    with lock:
        for client in clients:
            if client != sender:
                send_json(client["sock"], message)

def handle_client(client):
    sock = client["sock"]
    username = client["username"]

    join_msg = f"[{timestamp()}] {username} joined."
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

    except:
        pass
    finally:
        with lock:
            if client in clients:
                clients.remove(client)

        leave_msg = f"[{timestamp()}] {username} left."
        logging.info(leave_msg)
        print(leave_msg)
        broadcast({"type": "sys", "msg": leave_msg})

        sock.close()

def host_input_loop(username):
    while True:
        try:
            msg = input()
        except EOFError:
            break

        if msg.strip() == "/quit":
            print("Shutting down host...")
            break

        full_msg = f"[{timestamp()}] {username}: {msg}"
        logging.info(full_msg)
        print(full_msg)

        broadcast({"type": "msg", "msg": full_msg})

def run_host(port, password, username):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("0.0.0.0", port))
    server.listen(10)

    print(f"[{timestamp()}] Host '{username}' listening on port {port}")

    threading.Thread(target=host_input_loop, args=(username,), daemon=True).start()

    while True:
        sock, addr = server.accept()

        try:
            auth = recv_json(sock)

            if not auth or auth.get("type") != "auth":
                sock.close()
                continue

            client_username = auth.get("username", "").strip()
            client_pass = auth.get("password")

            # ---- Username validation only ----
            if not client_username:
                send_json(sock, {"type": "sys", "msg": "Invalid username"})
                sock.close()
                continue

            # ---- Password check ----
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

# ---------- Client Logic ----------

def receive_loop(sock):
    while True:
        data = recv_json(sock)
        if not data:
            print("Disconnected from server.")
            break

        msg = data.get("msg", "")
        print(msg)

        if data["type"] == "msg":
            notify("New Message", msg)

def run_client(target, port, username, password):
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

    sock.settimeout(2)
    try:
        response = recv_json(sock)
        if response and response.get("type") == "sys":
            print(response.get("msg"))
            sock.close()
            return
    except:
        pass
    finally:
        sock.settimeout(None)

    threading.Thread(target=receive_loop, args=(sock,), daemon=True).start()

    print(f"Connected as {username}. Type /quit to exit.")

    while True:
        try:
            msg = input()
        except EOFError:
            break

        if msg.strip() == "/quit":
            break

        send_json(sock, {
            "type": "msg",
            "msg": msg
        })

    sock.close()
    print("Disconnected.")

# ---------- Main ----------

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("--dev", required=True, choices=["host", "client"])
    parser.add_argument("--target", help="Host IP (client mode)")
    parser.add_argument("--port", type=int, default=5000)
    parser.add_argument("--username", help="Username (required)")
    parser.add_argument("--password", default=None)
    parser.add_argument("--log", default="chat.log")

    args = parser.parse_args()

    logging.basicConfig(
        filename=args.log,
        level=logging.INFO,
        format="%(asctime)s %(message)s"
    )

    if not args.username:
        print("You must provide --username")
        return

    if args.dev == "host":
        run_host(args.port, args.password, args.username.strip())

    elif args.dev == "client":
        if not args.target:
            print("Client mode requires --target")
            return

        run_client(args.target, args.port, args.username.strip(), args.password)

if __name__ == "__main__":
    main()
