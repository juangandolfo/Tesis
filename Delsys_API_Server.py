import socket
import random
import json
import time
import pickle
import numpy as np
import clr  
clr.AddReference("System")
from System import Guid  



HOST = "127.0.0.1"  # Standard adress (localhost)
PORT = 6001  # Port to listen on (non-privileged ports are > 1023)


def FormattedDictionary_to_PythonDictionary(formatted_dictionary):
    python_dictionary = {}
    #outArr = [[] for i in range(len(formatted_dictionary.Keys))] # matrix
    keys = []

    for i in formatted_dictionary.Keys:
        keys.append(i)
    for j in range(len(keys)):
        #outArr[j].append(np.asarray(formatted_dictionary[keys[j]], dtype='object'))
        python_dictionary[str(keys[j])] = np.asarray(formatted_dictionary[keys[j]]).tolist()

    return python_dictionary


def API_Server(AeroInstance):
    # Create a socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:

        # Link the socket to the IP and PORT selected: 
        s.bind((HOST, PORT))

        # Listen the inner connections:
        print("Delsys API Server listening on", HOST, "port", PORT)
        s.listen()
        
        # Accept the connection and open a socket to receive and send data. 
        conn, addr = s.accept()
        with conn:
            print(f"Connected by {addr}")
            while True:
                data = conn.recv(1024)
                # Check if the received data is a GET request for "/data"
                if data.decode().strip() == "GET /data":
                    dataReady = AeroInstance.CheckDataQueue()
                    if dataReady: 
                        response_data = FormattedDictionary_to_PythonDictionary(AeroInstance.PollData())
                    else: 
                        response_data={}
                    serialized_data = json.dumps(response_data) # Serialize the object using json
                    serialized_data  += "#DELIMITER#" # Add a delimiter at the end 
                    conn.sendall(serialized_data.encode())
                    #print("Data sent:", serialized_data)
                    """
                elif data.decode().strip() == "GET /NumberSensors":
                    response_data = AeroInstance.GetNumberSensors()
                    serialized_data = json.dumps(response_data)
                    """
                else:
                   print("Invalid request")
                    





