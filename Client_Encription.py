# -*- coding: utf-8 -*-
"""
Created on Tue Apr 11 17:20:11 2023

@author: Morgen
"""
# Importing necessary cryptographic and networking libraries
from cryptography.fernet import Fernet
import socket
import sys
from hashlib import sha256
import os
import hashlib
import hmac
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import rsa
import random

# For RSA key generation (commented out because it's only needed once to generate keys)
'''
# Generating RSA public/private keys for the client (Bob)
client_public_key, client_private_key = rsa.newkeys(512)

# Saving the public key for server (Alice) to use during encryption
with open("C:/Users/Morgen/Desktop/client_public_key.pem", "+wb") as f:
    f.write(client_public_key.save_pkcs1())
    print(client_public_key.save_pkcs1(), "\n")

# Saving the private key for client (Bob) to decrypt messages
with open("C:/Users/Morgen/Desktop/client_private_key.pem", "+wb") as f:
    f.write(client_private_key.save_pkcs1())
    print(client_private_key.save_pkcs1(), "\n")
'''

# Reading the symmetric key (Fernet) from the file, which is shared between client and server
with open('C:/Users/Morgen/Desktop/SecureKey.txt', 'rb') as f:
    symmatrykey = f.read()  # The key is read from the file
symmatrykey = Fernet(symmatrykey)  # Creating a Fernet object to handle encryption/decryption

# Generating a random nonce (one-time random number) for challenge-response authentication
nonce = random.randint(1, 1000000)

# Encrypting the nonce using the symmetric key to securely send it to the server
challenge = symmatrykey.encrypt(str(nonce).encode())

# Reading the server's public RSA key from a file for encryption purposes
with open("C:/Users/Morgen/Desktop/server_public_key.pem", "rb") as f:
    server_public_key_data = f.read()
    server_public_key = rsa.PublicKey.load_pkcs1(server_public_key_data)

# Reading the client's private RSA key for decryption purposes
with open("C:/Users/Morgen/Desktop/client_private_key.pem", "rb") as f:
    client_private_key_data = f.read()
    client_private_key = rsa.PrivateKey.load_pkcs1(client_private_key_data)

# Reading the file that will be encrypted and sent to the server
with open('C:/Users/Morgen/Desktop/tomboy.txt', 'rb') as f:
    file_data = f.read()

# Encrypting the file using the server's public key so that only the server can decrypt it
sign_data_encrypt = rsa.encrypt(file_data, server_public_key)

# Saving the encrypted message to a file before sending it
with open("C:/Users/Morgen/Desktop/themessage.txt", "+wb") as f:
    f.write(sign_data_encrypt)
    data = sign_data_encrypt  # Assigning encrypted data to the 'data' variable for sending

# Setting up the socket to connect to the server (Alice)
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = ('192.168.1.66', 59710)  # Server's IP address and port number

try:
    # Connecting to the server (Alice)
    sock.connect(server_address)
    print("Connected to server")
    
    # Setting a timeout of 5 seconds for the server's response
    sock.settimeout(5)
    
    # Receiving the challenge (nonce) from the server and decrypting it
    challenge = sock.recv(1024)
    challenge_return = int(symmatrykey.decrypt(challenge).decode())  # Decrypt and decode the nonce
    challenge_return += 1  # Incrementing the nonce for the response
    
    # Sending the incremented nonce back to the server to prove identity
    sock.sendall(challenge_return)
    print("Sent response")
    
    # Sending the encrypted challenge to the server
    sock.sendall(challenge)
    
    # Receiving the server's response to Bob's challenge (incremented challenge)
    bob_challenge = sock.recv(1024)
    
    # Verifying if the server correctly incremented the challenge (server is Alice)
    if bob_challenge == challenge + 1:
        print("Server is verified to be Alice")
        
        # Sending the encrypted data (message) to the server
        connection.sendall(data)
        print("Data sent")
        
        # Receiving an encrypted file from the server
        received_file = connection.recv(1024)
        print('Received encrypted file from server')
        
    else:
        # If the challenge is incorrect, the client (Bob) terminates the connection
        print("Server is not Alice, terminating connection")
        sock.close()  # Closing the connection

# If no response is received within the timeout period, print an error message
except socket.timeout:
    print("Timed out waiting for response from server")

# Finally, close the socket connection when communication is done
finally:
    print('Closing socket')
    sock.close()
