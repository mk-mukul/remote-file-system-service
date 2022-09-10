import socket
import json

HEADER = 64
PORT = 5050
FORMAT = 'utf-8' # encode and decode format
DISCONNECT_MSG = "!DISCONNECT"
SERVER = 'acer.mkmukul.com'
ADDR = (SERVER, PORT)

client =  socket.socket(socket.AF_INET, socket.SOCK_STREAM)

client.connect(ADDR)
print(f"[CONNECTED] {ADDR} connected.")

def send(msg):
    message = msg.encode(FORMAT)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length)) #make the lenght of string of lenth 64 byte
    client.send(send_length)
    client.send(message)
    receive()

def receive():
    msg_length = client.recv(HEADER).decode(FORMAT)
    if msg_length:
        msg_length = int(msg_length)
        msg = client.recv(msg_length).decode(FORMAT)
        msg = json.loads(msg)
        print(f"{msg}")

connected = True

while connected:
    msg = str(input(f"{SERVER}:>>"))
    if msg == "exit":
        send(DISCONNECT_MSG)
        print(f"[DISCONNECTED] {ADDR} disconnected.")
        connected = False
    else:
        send(msg)

