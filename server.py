import socket
import threading
import os
import json
import time

HEADER = 64 # tells client that first 64 bytes is the number that tells number of bytes thats going to received 
# if msg length is more then 64 bytes the there is a problem to represent or tell the server

PORT = 5050
SERVER = 'acer.mkmukul.com'
# SERVER = socket.gethostbyname(socket.gethostname())
# print(socket.gethostname())
ADDR = (SERVER, PORT)
FORMAT = 'utf-8' # encode and decode format
DISCONNECT_MSG = "!DISCONNECT"

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
def tart():
    server.bind(ADDR)
tart()



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
        msg_length = conn.recv(HEADER).decode(FORMAT)
        if msg_length:
            msg_length = int(msg_length)
            msg = conn.recv(msg_length).decode(FORMAT)
            if msg == DISCONNECT_MSG:
                connected = False
                send(conn, addr, "Connection closed form the server")
                break
            print(f"[{addr}] {msg}")
            return_msg = handle_command(conn, addr, msg)
            send(conn, addr, return_msg)
    conn.close()
    # print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 2}")

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
            return "Invalid argument"
        if command[1] in os.listdir():
            os.chdir(command[1])
            return os.getcwd()
        elif command[1] == "../":
            os.chdir(command[1])
            return os.getcwd()
        else:
            return "Directory not present"

    if command[0] == "dwd":
        if len(command) < 2:
            return "Invalid argument"
        return send_file(conn, addr, command[1])

    if command[0] == "upd":
        if len(command) < 2:
            return "Invalid argument"
        return load_file(conn, addr, command[1])

    return "Invalid command"


def send(conn, addr, msg):
    send_msg = json.dumps(msg)
    msg_length = len(send_msg)
    send_length = str(msg_length).encode(FORMAT)
    # print(f"Send length: {send_length} || lenght of send lenght: {len(send_length)}")
    send_length += b' ' * (HEADER - len(send_length))
    # print(len(send_length))

    conn.send(send_length)
    conn.send(send_msg.encode(FORMAT))

def send_file(conn, addr, file_name):
    # print(file_name)
    if file_name in os.listdir():
        if os.path.isfile(file_name):
            print("Sending file...")
            send(conn, addr, "File sending...")
            send(conn, addr, file_name)
            file_size = os.path.getsize(file_name)
            print(file_size)
            send(conn, addr, file_size)
            with open(file_name, mode='r', encoding='utf-8') as file:
                c = 0
                start_time = time.time()
                # while c <= file_size:
                data = file.read()
                # if not data:
                #     break
                send(conn, addr, data)
                    # c+=len(data)
                end_time = time.time()
                total_time = end_time - start_time
            print(f"File sent to {addr} in {total_time}")
            return "File send in " + str(total_time)
    return "File not present"

def load_file(conn, addr, file_name):
    print(file_name)
    return "file not received"

print("[STARTING] server is starting...")
start()

