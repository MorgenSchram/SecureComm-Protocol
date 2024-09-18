# -*- coding: utf-8 -*-
"""
Created on Tue Apr 18 19:22:39 2023

@author: Morgen
"""
# Importing necessary cryptography and networking libraries
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

# For key generation (commented out as it's only needed once)
'''
server_public_key, server_private_key = rsa.newkeys(512)  # Generate RSA key pair
with open("C:/Users/Morgen/Desktop/server_public_key.pem", "+wb") as f:  # Save public key
    f.write(server_public_key.save_pkcs1())
    print(server_public_key.save_pkcs1())
with open("C:/Users/Morgen/Desktop/server_private_key.pem", "+wb") as f:  # Save private key
    f.write(server_private_key.save_pkcs1())
    print(server_private_key.save_pkcs1())
'''

# Generate a symmetric key with Fernet (commented out as the key has already been generated)
'''
securekey = Fernet.generate_key()
'''

# Reading the symmetric key from the file where it was saved earlier
with open('C:/Users/Morgen/Desktop/SecureKey.txt', 'rb') as f:
    symmatrykey = f.read()  # The file contains the Fernet key
symmatrykey = Fernet(symmatrykey)  # Load the symmetric key for encryption and decryption

# Generating a random nonce (a unique number used once) for challenge-response
nonce = random.randint(1, 1000000)  
# Encrypting the nonce using the symmetric key for secure transmission
challenge = symmatrykey.encrypt(str(nonce).encode())  

# Reading the client's public RSA key from a file for encryption purposes
with open("C:/Users/Morgen/Desktop/client_public_key.pem", "rb") as f:
    client_public_key_data = f.read()
    client_public_key = rsa.PublicKey.load_pkcs1(client_public_key_data)

# Reading the server's private RSA key from a file for decryption and signing
with open("C:/Users/Morgen/Desktop/server_private_key.pem", "rb") as f:
    server_private_key_data = f.read()
    server_private_key = rsa.PrivateKey.load_pkcs1(server_private_key_data)

# Reading a file to be encrypted and signed (message)
with open('C:/Users/Morgen/Desktop/tomboy2.txt', 'rb') as f:
    file_data = f.read()

# Encrypting the file with the client's public key (ensuring only the client can decrypt it)
sign_data_encrypt = rsa.encrypt(file_data, client_public_key)
print(sign_data_encrypt, "\n")

# Saving the encrypted data to a file for future transmission
with open("C:/Users/Morgen/Desktop/themessage2.txt", "+wb") as f:
    f.write(sign_data_encrypt)
    data = sign_data_encrypt  # Assigning encrypted data to 'data' variable for sending later

# Setting up the socket for network communication (server side)
socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = ('192.168.1.66', 59710)  # Server IP address and port
print('Starting up on {} port {}'.format(*server_address))

# Binding the server to the address and port
socket.bind(server_address)

# Start listening for incoming connections
socket.listen(1)

# Infinite loop to wait for incoming connections
while True:
    print('Waiting for a connection')
    connection, client_address = socket.accept()  # Accept a connection from a client
    
    try:
        print('Connection from', client_address)  # Print the client's address
        
        # Send the nonce to the client for the challenge-response protocol
        connection.sendall(nonce)
        print('Nonce sent')
        
        # Receive the response from the client (the incremented nonce)
        nonce_return = connection.recv(1024)
        
        # Check if the client correctly incremented the nonce, verifying the client's authenticity
        if nonce == nonce_return + 1:
            print("Client is verified to be Bob")  # Client successfully verified
            
            # Send the encrypted data (proving server authenticity as Alice)
            connection.sendall(data)  # moved this line inside the if statement
            print("Proving to client that I am Alice")
            
            # Receive and decrypt the client's challenge (proving client's authenticity again)
            challenge2 = connection.recv(1024)
            challenge_return = int(symmatrykey.decrypt(challenge2).decode())  # Decrypt the challenge
            connection.sendall(challenge_return)  # Send the decrypted value back to the client
            print("Data sent")
            
            # Receive the encrypted file from the client (possibly the signed message)
            received_file = connection.recv(1024)
            print('Received encrypted file from client')
        
        # If the nonce check fails, the client is not recognized as Bob, terminate connection
        else:
            print("Client is not Bob, terminating connection")
            socket.close()  # Close the connection for security reasons
    
    finally:
        # Close the socket connection after the communication is finished or if an error occurs
        print('Closing socket')
        socket.close()
        break  # Break the loop to stop the server
