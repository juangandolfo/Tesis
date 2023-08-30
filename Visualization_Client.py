import socket
import time
import json
import numpy as np
from collections import deque
from threading import Thread, Semaphore

HOST = "127.0.0.1"  # The server's hostname or IP address
PORT2 = 6002  # The port used by the API server


# Create a socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT2))

# List to save the received data
data_stack = deque()
stack_lock = Semaphore(1)  # Semaphore for stack access

# Function to send the request and receive the data
def Get_data():
        request = "GET /data"
        client_socket.sendall(request.encode())
        data = client_socket.recv(1024)
        response_data = json.loads(data.decode()) # Decode the received data
        return response_data
     

# Loop to send the request and save the data 
while True:
        try:
             data = Get_data()
             #stack_lock.acquire()  # Acquire lock before accessing the stack
             #data_stack.extend(data)  
             print(f"Received {data!r}")  
             #stack_lock.release()  # Release lock after reading the stack
             time.sleep(0.017)   

        except socket.error as e:
             print("Connection error:", e)
             # Manage a connection error 


