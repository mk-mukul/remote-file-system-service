import socket
import json
import time
import os

HEADER = 64
PORT = 5050
SERVER = 'acer.mkmukul.com'
ADDR = (SERVER, PORT)
FORMAT = 'utf-8' # encode and decode format

client =  socket.socket(socket.AF_INET, socket.SOCK_STREAM)

client.connect(ADDR)
print(f"[CONNECTED] {ADDR} connected.")


def send(msg):
    send_msg = json.dumps(msg)
    msg_length = len(send_msg)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length)) # to make string 64 byte
    client.send(send_length)
    client.send(send_msg.encode(FORMAT))


def receive():
    data_length = client.recv(HEADER).decode(FORMAT)
    if data_length:
        data_length = int(data_length)
        data = client.recv(data_length).decode(FORMAT)
        data = json.loads(data)
        return data


def download_file():
    print(f"File downloading from {SERVER}")
    print(f"Downloading...")
    file_name = receive()
    file_size = receive()
    time.sleep(1)
    with open("./"+file_name, mode='w', encoding='utf-8') as file:
        start_time = time.time()
        data = receive()
        file.write(data)
        end_time = time.time()
        total_time = end_time - start_time
    print(f"File received from {SERVER} in {total_time} seconds")
    return 1


def upload_file(file_name): 
    print(f"File uploading...")     
    send(file_name)
    file_size = os.path.getsize(file_name)
    send(file_size)
    with open(file_name, mode='r', encoding='utf-8') as file:
        start_time = time.time()
        data = file.read()
        send(data)
        end_time = time.time()
        total_time = end_time - start_time
    print(f"File uploaded to {SERVER} in {total_time} seconds")
    return 1
    

connected = True
while connected:
    msg = str(input(f"{SERVER}:~>> "))

    if msg == "exit":
        send(msg)
        print(f"[DISCONNECTED] {ADDR} disconnected.")
        print(receive())
        client.close()
        connected = False
        break

    if msg.split()[0] == "upd":
        if msg.split()[1] in os.listdir():
            if os.path.isfile(msg.split()[1]):
                send(msg)
                upload_file(msg.split()[1])
                print("Status: ", receive())
                continue
            else:
                print("File not present")
                continue
        else:
            print("File not present")
            continue

    send(msg)
    data = receive()
    if type(data)==list:
        for i in data:
            print(f"{i}", end="\t")
        print()
    elif data == "File sending...":
        download_file()
        print("Status: ", receive())
    else:
        print(data)
        

