import socket
import json
import time
import os

# ################### Edit according to your need #########################
SERVER = 'acer.mkmukul.com' # name or ip address of the server ############
PORT = 5050                 # port on which server will run ###############
# #########################################################################

ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
HEADER = 64 # header size used
CAESAR_OFFSET = 5 # offset used by caesar cipher
ENC_MODE = 0 # default encryption mode

# take encryption mode from the user
enc_selected = input(f"Encreption mode:\n0-> Plain Text (Default)\n1-> Caesar cipher with offset {CAESAR_OFFSET}\n2-> Transpose\nSelect encreption mode: ")
if enc_selected=="0" or enc_selected=="1" or enc_selected=="2":
    ENC_MODE = int(enc_selected)
elif enc_selected:
    print("Invalid encreption mode selected.")
    exit()


client =  socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# start the connection
def start():
    try:
        client.connect(ADDR)
    except:
        print(SERVER, " not found.")
        return
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
        
# analysis command and send to the server
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
            show_status(receive())
            return
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

# show command status
def show_status(status):
    if status:
        print(f"Status: OK")
    else: 
        print(f"Status: NOK")

def transpose(data):
    transpose_data = ""
    i = 0
    temp = ""
    while i < len(data):
        if not data[i].isalpha():
            if temp:
                transpose_data += transpose_word(temp)
                temp=""
            transpose_data += data[i]
        else:
            temp += data[i]
        i+=1
    if temp:
        transpose_data += transpose_word(temp)
        temp=""        
    return transpose_data

def transpose_word(data):
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

# send data tot he server 
def send(data):
    try:
        enc_mode = ENC_MODE
        # conver the data into json string 
        send_data = json.dumps(data)
        # encrypt message and add encryption mode as a header
        enc_data = str(enc_mode) + encryption(send_data, enc_mode)
        data_length = len(enc_data)
        send_length = str(data_length).encode(FORMAT)
        send_length += b' ' * (HEADER - len(send_length))
        # send the lenght of message to be transmitted in 64 bytes
        client.send(send_length)
        # send the data
        client.send(enc_data.encode(FORMAT))
        return
    except:
        return

#  receive data form the server
def receive():
    try:
        # get the lenght of data to be received next
        data_length = client.recv(HEADER).decode(FORMAT)
        if data_length:
            data_length = int(data_length)
            # received the encrypted data
            enc_data = client.recv(data_length).decode(FORMAT)
            # decrypt the data on the basis of encryption mode
            data = decryption(enc_data[1:], int(enc_data[0]))
            # loads the data in its original form
            data = json.loads(data)
            return data
    except:
        return

# download file form the server
def download_file():
    try:
        print(f"File downloading from {SERVER}")
        print(f"Downloading...")
        file_name = receive()
        file_size = receive()
        with open("./"+file_name, 'wb') as file:
            start_time = time.time()
            while True:
                buffer = receive()
                if not buffer:
                    break
                file_data = bytes(receive(), encoding="utf-8")
                file.write(file_data)
            end_time = time.time()
            total_time = end_time - start_time
        print(f"File downloaded from {SERVER} in {round(total_time, 5)} seconds")
    except:
        print(f"Some error in dowloading file from {SERVER}.")

# upload file to the server
def upload_file(file_name):
    try: 
        print(f"File uploading...")     
        send(file_name)
        file_size = os.path.getsize(file_name)
        send(file_size)
        with open("./"+file_name, 'rb') as file:
            start_time = time.time()
            while True:
                file_data = file.read(1024)
                buffer = len(file_data)
                send(buffer)
                if not buffer:
                    break
                send(str(file_data, encoding="utf-8"))
            end_time = time.time()
            total_time = end_time - start_time
        print(f"File uploaded to {SERVER} in {round(total_time, 5)} seconds")
    except:
        print(f"Some error in uploading file to {SERVER}.")

#  start the client
start()

# ############################# END ###########################