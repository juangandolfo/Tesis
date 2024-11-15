import socket
import json
import time
import numpy as np
from collections import deque
from threading import Thread, Semaphore
import LocalCircularBufferVector as Buffer




HOST = "127.0.0.1"  # Standard adress (localhost)
PORT_Client = 6001  # Port to get data from the API Server
PORT_Server = 6002 # The port used by the PM Server


# Create a socket for the client 
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Create a socket for the server
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Link the socket to the IP and PORT selected: 
server_socket.bind((HOST, PORT_Server))


# List to save the received data 
BufferSize = 10000
NumberChannels = 9
#data_stack = deque() 
circular_stack = Buffer.CircularBufferVector(BufferSize, NumberChannels)
stack_lock = Semaphore(1)  # Semaphore for stack access



# Auxiliar functions -------------------------------------------------------------------------------------------------------------------------------------------------------------

def Dictionary_to_matrix(dictionary):
    
    # Get the keys
    columns = list(dictionary.keys())
    # Get the data 
    rows = [dictionary[column] for column in columns]
    matriz = np.array(rows).T 
    #rows = np.array(rows)
    
    return matriz

# Function to send the request and receive the data from API Server
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
        time.sleep(2)    
        if response_data == {}:
            raise Exception("No data received")
        return response_data

# Function to handle the connection with a client
def Handle_Client(conn,addr):
    print(f"Connected by {addr}")
    #Connected = True
    while True:
        data = conn.recv(1024)
        # Check if the received data is a GET request for "/data"
        if  data.decode().strip() == "GET /data1":
            stack_lock.acquire()  # Acquire lock before accessing the stack
            response_data = circular_stack.get_oldest_vector(1)
            #print(response_data)
            stack_lock.release()  # Release lock after reading the stack
                     
            if len(response_data) == 0:
                response_data = [0,0,0,0,0,0,0,0,0]
                         
            response_data = np.array(response_data).tolist()
            response_json = json.dumps(response_data).encode()  # Convert the dictionary to JSON and enconde intio bytes
            conn.sendall(response_json)
            #print("Data sent:", response_json)

        elif  data.decode().strip() == "GET /data2":
            stack_lock.acquire()  # Acquire lock before accessing the stack
            response_data = circular_stack.get_oldest_vector(2)
            #print(response_data)
            stack_lock.release()  # Release lock after reading the stack
                     
            if len(response_data) == 0:
                response_data = [0,0,0,0,0,0,0,0,0]
                         
            response_data = np.array(response_data).tolist()
            response_json = json.dumps(response_data).encode()  # Convert the dictionary to JSON and enconde intio bytes
            conn.sendall(response_json)
            #print("Data sent:", response_json)
        
        #if data.decode().strip() == "DISCONNECT":
             #Connected = False

        else:
            print("Invalid request") 
    #conn.close()                        
        
# ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Threads -------------------------------------------------------------------------------------------------------------------------------------------------------------------------
               
def Processing_Module_Client():
    global data_stack
    client_socket.connect((HOST, PORT_Client))
    
     # Loop to send the request and save the data 
    while True:
            try:
                try:
                    data = Get_data()
                except Exception as e:
                    print(e)
                    continue
                formated_data = Dictionary_to_matrix(data)
                stack_lock.acquire()  # Acquire lock before accessing the stack
                #data_stack.extend(formated_data) # If we use TCP/IP between the PM and the visualization app. 
                circular_stack.add_matrix(formated_data)
                #print(circular_stack.get_vectors())
                #data_stack = [np.concatenate((vector, row)) for vector, row in zip(data_stack, formated_data)] # If we use shared memory between the PM and the visualization app. We can avoid the 'for' using the transpose matrix (above line). 
                #print(f"Received {data_stack!r}") 
                stack_lock.release()  # Release lock after reading the stack
                #time.sleep(1)   
            except socket.error as e:
                print("Connection error:", e)
                # Manage a connection error 


def Processing_Module_Server():

        # Listen the inner connections:
        print("Server listening on", HOST, "port", PORT_Server)
        server_socket.listen()
        Num_Clients = 0
        
        while Num_Clients < 2:
             # Accept the connection and open a thread to handle the client. 
             conn, addr = server_socket.accept()
             thread = Thread(target = Handle_Client, args=(conn, addr))
             thread.start()
             Num_Clients = Num_Clients + 1
             #print(Num_Clients)

                    
    



