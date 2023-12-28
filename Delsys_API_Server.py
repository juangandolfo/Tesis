import socket
import random
import json
import time
import pickle
from DataCollector.CollectDataController import *

HOST = "127.0.0.1"  # Standard adress (localhost)
PORT = 6001  # Port to listen on (non-privileged ports are > 1023)


def FormattedDictionary_to_PythonDictionary(formatted_dictionary):
    python_dictionary = {}
    for key in formatted_dictionary.Keys:
        python_dictionary[key] = formatted_dictionary[key]
    
    return python_dictionary

def API_Server():
    # Create a socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:

        # Link the socket to the IP and PORT selected: 
        s.bind((HOST, PORT))

        # Listen the inner connections:
        print("Server listening on", HOST, "port", PORT)
        s.listen()
        
        # Accept the connection and open a socket to receive and send data. 
        conn, addr = s.accept()
        with conn:
            print(f"Connected by {addr}")
            while True:
                data = conn.recv(1024)
                # Check if the received data is a GET request for "/data"
                if data.decode().strip() == "GET /data":
                    dataReady = TrigBase.CheckDataQueue()
                    if dataReady: 
                        response_data = FormattedDictionary_to_PythonDictionary(TrigBase.PollData())
                    else: 
                        response_data={}
                    serialized_data = pickle.dumps(response_data) # Serialize the object using pickle
                    serialized_data  += b"#DELIMITER#" # Add a delimiter at the end 
                    conn.sendall(serialized_data)
                        #print("Data sent:", serialized_data)
                else:
                   print("Invalid request")
                    





