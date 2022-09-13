import socket
import os
import json
import time

SERVER = 'acer.mkmukul.com'
PORT = 5050
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
HEADER = 64
ENC_MODE = 0
CAESAR_OFFSET = 5


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


def bind_server(ADDR):
    server.bind(ADDR)
bind_server(ADDR)


def start():
    server.listen()
    print(f"[LISTENING] Server is listening on {SERVER}")
    while True:
        conn, addr = server.accept()
        enc_mode = receive(conn, addr)
        handle_client(conn, addr, enc_mode)


def handle_client(conn, addr, enc_mode):
    global ENC_MODE 
    ENC_MODE = enc_mode
    print(f"[NEW CONNECTION] {addr} connected with encreption mode {ENC_MODE}.")
    connected = True
    while connected:
        print(f"[{addr}]", end=" ")
        cmd = receive(conn, addr)
        print(f"{cmd}")
        if cmd == "exit":
            connected = False
            break
        returning_data = handle_command(conn, addr, cmd)
        send(conn, addr, returning_data)

    send(conn, addr, "Connection closed form the server")
    conn.close()
    print(f"[DISCONNECTED] {addr} disconnected")


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

def send(conn, addr, data):
    try:
        enc_mode = ENC_MODE    
        send_data = json.dumps(data)
        enc_data = encryption(send_data, enc_mode)
        data_length = len(enc_data)
        send_length = str(data_length).encode(FORMAT)
        send_length += b' ' * (HEADER - len(send_length))
        conn.send(str(enc_mode).encode(FORMAT))
        conn.send(send_length)
        conn.send(enc_data.encode(FORMAT))
        return
    except:
        return

def receive(conn, addr):
    try:
        enc_mode = conn.recv(1).decode(FORMAT)
        if enc_mode:
            data_length = conn.recv(HEADER).decode(FORMAT)
            data_length = int(data_length)
            enc_data = conn.recv(data_length).decode(FORMAT)
            data = decryption(enc_data, int(enc_mode))
            data = json.loads(data)
            return data
    except:
        return



def handle_command(conn, addr, cmd):
    command = cmd.split()
    if not command:
        return ""
    if command[0] == "close":
        print(f"[CLOSING] server is closing...")
        send(conn, addr, "Server closed.")
        server.close()
        print(f"Server closed.")
        exit()
    if command[0] == "cwd":
        return os.getcwd()
    if command[0] == "ls":
        return os.listdir()
    if command[0] == "cd":
        if len(command) < 2:
            return 0
        if command[1] in os.listdir():
            if not os.path.isfile(command[1]):
                os.chdir(command[1])
                return 1
            else:
                return 0
        elif command[1] == "../":
            os.chdir(command[1])
            return 1
        else:
            return 0
    if command[0] == "dwd":
        if len(command) < 2:
            send(conn, addr, "Invalid argument")
            return 0
        if os.path.isfile(command[1]):
            send(conn, addr, "sending")
            return send_file(conn, addr, command[1])
        send(conn, addr, "File not present")
        return 0
    if command[0] == "upd":
        if len(command) < 2:
            return 0
        data = receive(conn, addr)
        if data == "sending":
            return receive_file(conn, addr)
        else:
            return 0
    send(conn, addr, "Invalid command")
    return 0


def send_file(conn, addr, file_name):
    try:
        print(f"Sending file to {addr}")
        print(f"Sending...")
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
        return 1
    except:
        print(f"Some error in sending file to {addr}.")
        return 0


def receive_file(conn, addr):
    try:
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
        return 1
    except:
        print(f"Some error in receving file form {addr}.")
        return 0


print(f"[STARTING] Server is starting...")
start()

