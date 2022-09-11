import socket
import json
import time

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
    data = receive()
    if type(data)==list:
        for i in data:
            print(f"{i}", end="\t")
        print()
        return
    print(data)
    if data == "File sending...":
        download_file()

def receive():
    msg_length = client.recv(HEADER).decode(FORMAT)
    if msg_length:
        msg_length = int(msg_length)
        msg = client.recv(msg_length).decode(FORMAT)
        msg = json.loads(msg)
        return msg

def download_file():
    file_name = receive()
    file_size = receive()
    print(file_name)
    print(file_size)
    time.sleep(1)
    with open("./rec/"+file_name, mode='w', encoding='utf-8') as file:
        c = 0
        start_time = time.time()
        # while c<1:
        data = receive()
        # if not data:
        #     break
        file.write(data)
        # c+=len(data)
        end_time = time.time()
        total_time = end_time - start_time
    print(f"File received in ", total_time)
    


connected = True
while connected:
    msg = str(input(f"{SERVER}:~>> "))
    if msg == "exit":
        send(DISCONNECT_MSG)
        print(f"[DISCONNECTED] {ADDR} disconnected.")
        client.close()
        connected = False
    else:
        send(msg)

