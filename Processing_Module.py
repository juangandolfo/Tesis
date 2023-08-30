import socket
import json
import time
import numpy as np
from collections import deque
from threading import Thread, Semaphore


HOST = "127.0.0.1"  # Standard adress (localhost)
PORT = 6001  # Port to listen on from the API server (non-privileged ports are > 1023)
PORT2 = 6002 # The port used by the PM server

# Create a socket for the client 
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# List to save the received data 
data_stack = deque()
stack_lock = Semaphore(1)  # Semaphore for stack access

# Create a socket for the server
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)



# Auxiliar functions -------------------------------------------------------------------------------------------------------------------------------------------------------------

def Dictionary_to_matrix(dictionary):
    
    # Get the keys
    columns = list(dictionary.keys())
    # Get the data 
    rows = [dictionary[column] for column in columns]
    matriz = np.array(rows).T 
    #rows = np.array(rows)
    
    return matriz

# Function to send the request and receive the data from client (PM) 
def Get_data():
        request = "GET /data"
        client_socket.sendall(request.encode())
        data = b''       
        while True:
            chunk = client_socket.recv(1024)
            data += chunk
            if b"#DELIMITER#" in data:
                break  # Delimiter finded

        data_json = data.decode().rstrip("#DELIMITER#") # Quit the delimiter and decode the received data
        response_data = json.loads(data_json) # Get the original data       
                
        return response_data

# ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


# Threads -------------------------------------------------------------------------------------------------------------------------------------------------------------------------
               
def Processing_Module_Client():
    global data_stack
    client_socket.connect((HOST, PORT))
    
     # Loop to send the request and save the data 
    while True:
            try:
                data = Get_data()
                formated_data = Dictionary_to_matrix(data)
                stack_lock.acquire()  # Acquire lock before accessing the stack
                data_stack.extend(formated_data) # If we use TCP/IP between the PM and the visualization app. 
                #data_stack = [np.concatenate((vector, row)) for vector, row in zip(data_stack, formated_data)] # If we use shared memory between the PM and the visualization app. We can avoid the 'for' using the transpose matrix (above line). 
                #print(f"Received {data_stack!r}") 
                stack_lock.release()  # Release lock after reading the stack
                #time.sleep(1)   

            except socket.error as e:
                print("Connection error:", e)
                # Manage a connection error 


def Processing_Module_Server():

    # Create a socket
    #with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:

        # Link the socket to the IP and PORT selected: 
        server_socket.bind((HOST, PORT2))

        # Listen the inner connections:
        print("Server listening on", HOST, "port", PORT2)
        server_socket.listen()
        
        # Accept the connection and open a socket to receive and send data. 
        conn, addr = server_socket.accept()
        with conn:
            print(f"Connected by {addr}")
            while True:
                data = conn.recv(1024)
                # Check if the received data is a GET request for "/data"
                if  data.decode().strip() == "GET /data":
                    stack_lock.acquire()  # Acquire lock before accessing the stack
                    response_data = data_stack.popleft()
                    stack_lock.release()  # Release lock after reading the stack
                    response_data = response_data.tolist()
                    response_json = json.dumps(response_data).encode()  # Convert the dictionary to JSON and enconde intio bytes
                    conn.sendall(response_json)
                    print("Data sent:", response_json)
                else:
                    # If the received data is not "GET /data", close the connection
                    print("Invalid request")
    

Processing_Module_Client_thread = Thread(target=Processing_Module_Client)
Processing_Module_Server_thread = Thread(target=Processing_Module_Server)

Processing_Module_Server_thread.start()
Processing_Module_Client_thread.start()


