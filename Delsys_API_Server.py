import socket
import random
import json
import time
import pickle
import numpy as np
import clr  
clr.AddReference("System")
from System import Guid  
import API_Parameters

HOST = "127.0.0.1"  # Standard adress (localhost)
PORT = 6001  # Port to listen on (non-privileged ports are > 1023)


def FormattedDictionary_to_PythonDictionary(formatted_dictionary, emgPositionVector):
    python_dictionary = {}
    #outArr = [[] for i in range(len(formatted_dictionary.Keys))] # matrix
    keys = []

    for i in formatted_dictionary.Keys:
        keys.append(i)
    
    '''for j in range(len(keys)): 
        #outArr[j].append(np.asarray(formatted_dictionary[keys[j]], dtype='object'))
        python_dictionary[str(keys[j])] = np.asarray(formatted_dictionary[keys[j]]).tolist()
        # full data
    '''
    for j in emgPositionVector:
        #outArr[j].append(np.asarray(formatted_dictionary[keys[j]], dtype='object')) # matrix
            python_dictionary[str(keys[j])] = np.asarray(formatted_dictionary[keys[j]]).tolist()
          
    return python_dictionary


def API_Server(AeroInstance,emgPositionVector):
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
                DataReceived = conn.recv(1024)
                # Check if the received data is a GET request for "/data"
                data = DataReceived.decode().strip()
                if data == "GET /data":
                    dataReady = AeroInstance.CheckDataQueue()
                    
                    if dataReady: 
                        response_data = FormattedDictionary_to_PythonDictionary(AeroInstance.PollData(),emgPositionVector)
                    else: 
                        response_data={}
                    
                    serialized_data = json.dumps(response_data) # Serialize the object using json
                    if API_Parameters.TerminateCalibrationFlag: 
                        serialized_data  += "TC" # Add a delimiter at the end
                        API_Parameters.TerminateCalibrationFlag = False 
                    
                    elif API_Parameters.CalibrationStageInitialized:

                            API_Parameters.CalibrationStageInitialized = False 
                            
                            if API_Parameters.CalibrationStage == 1:
                                serialized_data  += "CS1" # Add a delimiter at the end     
                            elif API_Parameters.CalibrationStage == 2:
                                serialized_data  += "CS2" # Add a delimiter at the end   
                            elif API_Parameters.CalibrationStage == 3: 
                                serialized_data  += "CS3" # Add a delimiter at the end
                    elif API_Parameters.CalibrationStageFinished: 
                         API_Parameters.CalibrationStageFinished = False
                         serialized_data  += "CSF" # Add a delimiter at the end   
                                 
                    else:
                        serialized_data  += "~" # Add a delimiter at the end 
                    
                    try:
                        conn.sendall(serialized_data.encode())
                        #print(serialized_data)
                    except Exception as e:
                        print(e)
                           
                    #print("Data sent:", serialized_data)
                    
                elif data == "GET /SensorsNumber":
                   
                    serialized_data = json.dumps(API_Parameters.ChannelsNumber)
                    serialized_data  += "~"
                    try:
                        conn.sendall(serialized_data.encode())
                        #print(serialized_data)
                    except Exception as e:
                        print(e)

                elif data == "GET /SampleRate":
                   
                    serialized_data = json.dumps(API_Parameters.SampleRate)
                    serialized_data  += "~"
                    try:
                        conn.sendall(serialized_data.encode())
                    except Exception as e:
                        print(e)

                else:
                   print("Invalid request")
                    





