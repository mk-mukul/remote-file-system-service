import socket
import threading
import os
import json

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
server.bind(ADDR)

def handle_command(cmd):
    command = cmd.split()
    if command[0] == "cwd":
        # print(type(os.getcwd()))
        return json.dumps(os.getcwd())
    if command[0] == "ls":
        # print(type(os.listdir()))
        return json.dumps(os.listdir())
    if command[0] == "cd":
        if len(command) < 2:
            return json.dumps("Invalid argument")
        if command[1] in os.listdir():
            os.chdir(command[1])
            return json.dumps(os.getcwd())
        elif command[1] == "../":
            os.chdir(command[1])
            return json.dumps(os.getcwd())
        else:
            return json.dumps("Directory not present")

    # if command[0] == "dwd"
    # if command[0] == "upd"
    return json.dumps("Invalid command")


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
                return_msg = json.dumps("Connection closed form the server")
                msg_length = len(return_msg)
                send_length = str(msg_length).encode(FORMAT)
                send_length += b' ' * (HEADER - len(send_length)) 
                conn.send(send_length)
                conn.send(return_msg.encode(FORMAT))
                break
            print(f"[{addr}] {msg}")
            return_msg = handle_command(msg)
            msg_length = len(return_msg)
            send_length = str(msg_length).encode(FORMAT)
            #make the lenght of string of lenth 64 byte
            send_length += b' ' * (HEADER - len(send_length)) 
            conn.send(send_length)
            conn.send(return_msg.encode(FORMAT))
    conn.close()
    print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 2}")

def start():
    server.listen(1)
    print(f"[LISTENING] Server is listening on {SERVER}")
    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")

print("[STARTING] server is starting...")
start()

