import socket
import threading
import os
import json
import time

HEADER = 64 
PORT = 5050
SERVER = 'acer.mkmukul.com'
ADDR = (SERVER, PORT)
FORMAT = 'utf-8' # encode and decode format

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


def bind_server(ADDR):
    server.bind(ADDR)
bind_server(ADDR)


def start():
    server.listen(1)
    print(f"[LISTENING] Server is listening on {SERVER}")
    while True:
        conn, addr = server.accept()
        handle_client(conn, addr)
        # thread = threading.Thread(target=handle_client, args=(conn, addr))
        # thread.start()
        # print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")


def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr} connected.")
    connected = True
    while connected:    
        data = receive(conn, addr)
        if data == "exit":
            connected = False
            send(conn, addr, "Connection closed form the server")
            break
        print(f"[{addr}] {data}")
        return_data = handle_command(conn, addr, data)
        send(conn, addr, return_data)
    conn.close()
    print(f"[DISCONNECTED] {addr} disconnected")
    # print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 2}")


def send(conn, addr, msg):
    send_msg = json.dumps(msg)
    msg_length = len(send_msg)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))
    conn.send(send_length)
    conn.send(send_msg.encode(FORMAT))


def receive(conn, addr):
    data_length = conn.recv(HEADER).decode(FORMAT)
    if data_length:
        data_length = int(data_length)
        data = conn.recv(data_length).decode(FORMAT)
        data = json.loads(data)
        return data


def handle_command(conn, addr, cmd):
    command = cmd.split()

    if not command:
        return ""

    if command[0] == "cwd":
        return os.getcwd()

    if command[0] == "ls":
        return os.listdir()

    if command[0] == "cd":
        if len(command) < 2:
            return "Status: NOK"
        if command[1] in os.listdir():
            os.chdir(command[1])
            return "Status: OK"
        elif command[1] == "../":
            os.chdir(command[1])
            return "Status: OK"
        else:
            return "Directory not present\nStatus: NOK"

    if command[0] == "dwd":
        if len(command) < 2:
            return "Invalid argument"
        if command[1] in os.listdir():
            if os.path.isfile(command[1]):
                return send_file(conn, addr, command[1])
        return "File not present"

    if command[0] == "upd":
        if len(command) < 2:
            return "Invalid argument"
        return receive_file(conn, addr)

    return "Invalid command"


def send_file(conn, addr, file_name):
    print(f"Sending file to {addr}")
    print(f"Sending...")
    send(conn, addr, "File sending...")
    send(conn, addr, file_name)
    file_size = os.path.getsize(file_name)
    send(conn, addr, file_size)
    with open(file_name, mode='r', encoding='utf-8') as file:
        start_time = time.time()
        data = file.read()
        send(conn, addr, data)
        end_time = time.time()
        total_time = end_time - start_time
    print(f"File send to {addr} in {total_time} seconds")
    print("Status: OK")
    return "OK"


def receive_file(conn, addr):
    print(f"Receiving file form {addr}")
    print(f"Receving...")
    file_name = receive(conn, addr)
    file_size = receive(conn, addr)
    with open("./"+file_name, mode='w', encoding='utf-8') as file:
        start_time = time.time()
        data = receive(conn, addr)
        file.write(data)
        end_time = time.time()
        total_time = end_time - start_time
    print(f"File received form {addr} in {total_time} seconds")
    print("Status: OK")
    return "OK"


print("[STARTING] server is starting...")
start()

