from  GlobalParameters import *
import socket
import json
import time
import pickle
import numpy as np
from threading import Thread, Semaphore
import LocalCircularBufferVector as Buffer


HOST = "127.0.0.1"  # Standard adress (localhost)
PORT_Client = 6001  # Port to get data from the File API Server
PORT_Server = 6002 # The port used by the PM Server


# Create a socket for the client 
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Create a socket for the server
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Link the socket to the IP and PORT selected: 
server_socket.bind((HOST, PORT_Server))


# List to save the received data 
BufferSize = 1000
NumberChannels = 2 
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
    #matriz = np.array(dictionary[columns]).T
    #print(matriz)        
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
        
    serialized_data = data.decode().rstrip("#DELIMITER#") # Quit the delimiter and decode the received data
    response_data = json.loads(serialized_data) # Get the original data 
    #print(response_data)  
     
    if response_data == {}:
        raise Exception("PM:No data received")
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
                     
            if NumberChannels == 1:
                if response_data == None:
                    response_data = 0
            else:
                if all(element is None for element in response_data):
                    print("Empy buffer sample")
                    response_data = [0 for i in range(NumberChannels)]
                         
            response_data = np.array(response_data).tolist()
            response_json = json.dumps(response_data).encode()  # Convert the dictionary to JSON and enconde intio bytes
            conn.sendall(response_json)
            #print("PM: Data sent:", response_data)
            

        elif  data.decode().strip() == "GET /data2":
            stack_lock.acquire()  # Acquire lock before accessing the stack
            response_data = circular_stack.get_oldest_vector(2)
            #print(response_data)
            stack_lock.release()  # Release lock after reading the stack
            
            if NumberChannels == 1:
                if response_data == None:
                    response_data = 0
            else:
                if len(response_data) == 0:
                    response_data = [0 for i in range(NumberChannels)]

            response_data = np.array(response_data).tolist()
            response_json = json.dumps(response_data).encode()  # Convert the dictionary to JSON and enconde intio bytes
            conn.sendall(response_json)
            print("Data sent:", response_data)
        
        #if data.decode().strip() == "DISCONNECT":
             #Connected = False

        else:
            print("Invalid request") 
    #conn.close()                        
        
# ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Threads -------------------------------------------------------------------------------------------------------------------------------------------------------------------------
               
def Processing_Module_Client():
    client_socket.connect((HOST, PORT_Client))
    print("PM Client connected")
     # Loop to send the request and save the data 
    while True:
            try:
                try:
                    data = Get_data()
                except Exception as e:
                    print(e)
                    continue
                formated_data = Dictionary_to_matrix(data)
                #print(formated_data)
                       
                stack_lock.acquire()  # Acquire lock before accessing the stack
                circular_stack.add_matrix(formated_data)
                stack_lock.release()  # Release lock after reading the stack
                #time.sleep(0.5)  
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

                    
    



