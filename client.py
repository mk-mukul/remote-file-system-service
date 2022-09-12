import socket
import json
import time
import os

SERVER = 'acer.mkmukul.com'
PORT = 5050
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
HEADER = 64
CAESAR_OFFSET = 5
ENC_MODE = 0
end_selected = input(f"Encreption mode:\n0-> Plain Text (Default)\n1-> Caesar cipher with offset {CAESAR_OFFSET}\n2-> Transpose\nSelect encreption mode: ")

if end_selected:
    ENC_MODE = int(end_selected)



client =  socket.socket(socket.AF_INET, socket.SOCK_STREAM)


def start():
    client.connect(ADDR)
    send(ENC_MODE)
    print(f"[CONNECTED] Connected to server {ADDR} with encreption {ENC_MODE}.")  
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


def transpose(data):
    transpose_data = ""
    i = len(data)
    while i > 0:
        i-=1
        transpose_data+=data[i]
    return transpose_data

def caesar_encrypt(plainText, offset): 
    cipherText = ""
    for ch in plainText:
        if ch.isalpha():
            stayInAlphabet = ord(ch) + offset 
            if ch.islower():
                if stayInAlphabet > ord("z"):
                    stayInAlphabet -= 26
                finalLetter = chr(stayInAlphabet)
                cipherText += finalLetter
            else:
                if stayInAlphabet > ord("Z"):
                    stayInAlphabet -= 26
                finalLetter = chr(stayInAlphabet)
                cipherText += finalLetter
        
        elif ch.isnumeric():
            stayInNumeric = ord(ch) + offset
            if stayInNumeric > ord("9"):
                stayInNumeric -= 10
            finalLetter = chr(stayInNumeric)
            cipherText += finalLetter
        else:
            cipherText += ch
    return cipherText

def caesar_decrypt(cipherText, offset):
    plainText = ""
    for ch in cipherText:
        if ch.isalpha():
            stayInAlphabet = ord(ch) - offset 
            if ch.islower():
                if stayInAlphabet < ord("a"):
                    stayInAlphabet += 26
                finalLetter = chr(stayInAlphabet)
                plainText += finalLetter
            else:
                if stayInAlphabet < ord("A"):
                    stayInAlphabet += 26
                finalLetter = chr(stayInAlphabet)
                plainText += finalLetter
        elif ch.isnumeric():
            stayInNumeric = ord(ch) - offset
            if stayInNumeric < ord("0"):
                stayInNumeric += 10
            finalLetter = chr(stayInNumeric)
            plainText += finalLetter
        else:
            plainText += ch
    return plainText

def encryption(data, mode):
    if mode == 1:
        return caesar_encrypt(data, CAESAR_OFFSET)
    elif mode == 2:
        return transpose(data)
    return data

def decryption(data, mode):
    if mode == 1:
        return caesar_decrypt(data, CAESAR_OFFSET)
    elif mode == 2:
        return transpose(data)
    return data

def send(data):
    enc_mode = ENC_MODE
    send_data = json.dumps(data)
    enc_data = encryption(send_data, ENC_MODE)
    data_length = len(enc_data)
    send_length = str(data_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))
    client.send(str(enc_mode).encode(FORMAT))
    client.send(send_length)
    client.send(enc_data.encode(FORMAT))


def receive():
    enc_mode = client.recv(1).decode(FORMAT)
    if enc_mode:
        data_length = client.recv(HEADER).decode(FORMAT)
        data_length = int(data_length)
        enc_data = client.recv(data_length).decode(FORMAT)
        data = decryption(enc_data, int(enc_mode))
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

 
start()
