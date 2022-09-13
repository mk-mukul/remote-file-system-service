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
enc_selected = input(f"Encreption mode:\n0-> Plain Text (Default)\n1-> Caesar cipher with offset {CAESAR_OFFSET}\n2-> Transpose\nSelect encreption mode: ")

if enc_selected=="0" or enc_selected=="1" or enc_selected=="2":
    ENC_MODE = int(enc_selected)
elif enc_selected:
    print("Invalid encreption mode selected.")
    exit()


client =  socket.socket(socket.AF_INET, socket.SOCK_STREAM)


def start():
    client.connect(ADDR)
    send(ENC_MODE)
    print(f"[CONNECTED] Connected to server {ADDR} with encreption {ENC_MODE}.")  
    connected = True
    while connected:
        cmd = str(input(f"{SERVER}:~>> "))
        if not cmd:
            continue
        send(cmd)
        if cmd == "exit":
            connected = False
            break            
        handle_command(cmd)

    print(receive())
    client.close()
    print(f"[DISCONNECTED] {ADDR} disconnected.")
        

def handle_command(cmd):

    if cmd.split()[0] == "cwd":
        print(receive())
        return

    if cmd.split()[0] == "ls":
        data = receive()
        for i in data:
            print(f"\t{i}", end="")
        print()
        return

    if cmd.split()[0] == "cd":
        show_status(receive())
        return

    if cmd.split()[0] == "dwd":
        data = receive()
        if data == "sending":
            download_file()
        else:
            print(data)
        show_status(receive())
        return
    if cmd.split()[0] == "upd":
        if len(cmd.split()) < 2:
            print("Invalid argument")
        if os.path.isfile(cmd.split()[1]):
            send("sending")
            upload_file(cmd.split()[1])
        else:
            send("File not present")
            print("File not present")
        show_status(receive())
        return
    if cmd.split()[0] == "close":
        print(receive())
        exit()
    print(receive())
    receive()
    return


def show_status(status):
    if status:
        print(f"Status: OK")
    else: 
        print(f"Status: NOK")


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
    try:
        enc_mode = ENC_MODE
        send_data = json.dumps(data)
        enc_data = encryption(send_data, ENC_MODE)
        data_length = len(enc_data)
        send_length = str(data_length).encode(FORMAT)
        send_length += b' ' * (HEADER - len(send_length))
        client.send(str(enc_mode).encode(FORMAT))
        client.send(send_length)
        client.send(enc_data.encode(FORMAT))
        return
    except:
        return


def receive():
    try:
        enc_mode = client.recv(1).decode(FORMAT)
        if enc_mode:
            data_length = client.recv(HEADER).decode(FORMAT)
            data_length = int(data_length)
            enc_data = client.recv(data_length).decode(FORMAT)
            data = decryption(enc_data, int(enc_mode))
            data = json.loads(data)
            return data
    except:
        return



def download_file():
    try:
        print(f"File downloading from {SERVER}")
        print(f"Downloading...")
        file_name = receive()
        file_size = receive()
        with open("./"+file_name, mode='w', encoding='utf-8') as file:
            start_time = time.time()
            data = receive()
            file.write(data)
            end_time = time.time()
            total_time = end_time - start_time
        print(f"File downloaded from {SERVER} in {round(total_time, 5)} seconds")
    except:
        print(f"Some error in dowloading file from {SERVER}.")


def upload_file(file_name):
    try: 
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
        print(f"File uploaded to {SERVER} in {round(total_time, 5)} seconds")
    except:
        print(f"Some error in uploading file to {SERVER}.")

 
start()
