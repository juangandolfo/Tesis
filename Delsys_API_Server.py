import socket
import random
import json
import time
import msgpack as pack
import numpy as np
import clr
import pymsgbox as msgbox
import matplotlib.pyplot as plt
import zlib

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
        # outArr[j].append(np.asarray(formatted_dictionary[keys[j]], dtype='object'))
        # full data
    '''
    DataRows = min(set([len(formatted_dictionary[keys[i]]) for i in emgPositionVector]))
    DataColumns = len(emgPositionVector)
    OutMatrix = np.zeros((DataRows,DataColumns))
    for j in range(len(emgPositionVector)):
        OutMatrix[:,j] = np.asarray(formatted_dictionary[keys[emgPositionVector[j]]])[:DataRows]
    return OutMatrix.tolist()

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
            API_Parameters.CreateExperimentName()
            while True:
                #print("                                                 API Server live")
                try:
                    s.settimeout(5)
                    DataReceived = conn.recv(1024)
                except Exception as e:
                    print("API", e)
                # Check if the received data is a GET request for "/data"
                data = DataReceived.decode().strip()
                #print(data)
              
                if data == "GET /data":
                    dataReady = AeroInstance.CheckDataQueue()
                    if dataReady:
                        try:
                            response_data = FormattedDictionary_to_PythonDictionary(AeroInstance.PollData(),emgPositionVector)
                            #print(response_data)
                        except Exception as e:
                            msgbox.alert(f"Poll Data: {e}, {response_data}")
                    else:
                        response_data=[]
                    serialized_data = pack.packb(response_data,use_bin_type=True) # Serialize the object using msgpack

                    if API_Parameters.TerminateCalibrationFlag:
                        serialized_data  += b"TC" # Add a delimiter at the end
                        API_Parameters.TerminateCalibrationFlag = False

                    elif API_Parameters.CalibrationStageInitialized:
                            API_Parameters.CalibrationStageInitialized = False

                            if API_Parameters.CalibrationStage == 1:
                                serialized_data  += b"CS1" # Add a delimiter at the end
                            elif API_Parameters.CalibrationStage == 2:
                                serialized_data  += b"CS2" # Add a delimiter at the end
                            elif API_Parameters.CalibrationStage == 3:
                                serialized_data  += b"CS3" # Add a delimiter at the end
                            elif API_Parameters.CalibrationStage == 4:
                                serialized_data  += b"CS4" # Add a delimiter at the end

                    elif API_Parameters.CalibrationStageFinished:
                        API_Parameters.CalibrationStageFinished = False
                        serialized_data  += b"CSF" # Add a delimiter at the end
                        
                    else:
                        serialized_data += b'END' # Add a delimiter at the end
                        #print(serialized_data)
                    try:
                        conn.sendall(serialized_data)
                    except Exception as e:
                        print("API sending", e)

                elif data == "GET /SensorsNumber":
                    serialized_data = pack.packb(API_Parameters.ChannelsNumber, use_bin_type=True)
                    serialized_data  += b'END'
                    try:
                        conn.sendall(serialized_data)
                    except Exception as e:
                        print(e)

                elif data == "GET /SampleRate":
                    serialized_data = pack.packb(API_Parameters.SampleRate, use_bin_type=True)
                    serialized_data  += b'END'
                    try:
                        conn.sendall(serialized_data)
                    except Exception as e:
                        print(e)

                elif data == "GET /CalibrationTime":
                    serialized_data = pack.packb(API_Parameters.TimeCalibStage3, use_bin_type=True)
                    serialized_data  += b'END'
                    try:
                        conn.sendall(serialized_data)
                    except Exception as e:
                        print(e)

                elif data == "GET /Angles":
                    API_Parameters.AnglesOutputSemaphore.acquire()
                    serialized_data = pack.packb(API_Parameters.AnglesOutput, use_bin_type=True)
                    API_Parameters.AnglesOutputSemaphore.release()
                    serialized_data  += b'END'
                    try:
                        conn.sendall(serialized_data)
                    except Exception as e:
                        print(e)
                    dataReady = AeroInstance.CheckDataQueue()
                    if dataReady:
                        AeroInstance.PollData()
                
                elif data == "PLOT /Thresholds":
                    try:
                        serialized_data = pack.packb([1], use_bin_type=True)
                    except Exception as e:
                        msgbox.alert(e)
                    serialized_data  += b'END'
                    try:
                        conn.sendall(serialized_data)
                    except Exception as e:
                        print(e)
                    
                    data = conn.recv(1024)
                    API_Parameters.Thresholds = np.array(pack.unpackb(data.strip(), raw=False))
                    API_Parameters.PlotThresholds = True
                    try:
                        API_Parameters.PlotCalibrationSignal.signal.emit()
                    except Exception as e:
                        msgbox.alert(e)
                    serialized_data = pack.packb([1], use_bin_type=True)
                    try:
                        conn.sendall(serialized_data)
                    except Exception as e:
                        print(e)

                elif data == "PLOT /Peaks":
                    serialized_data = pack.packb([1], use_bin_type=True)
                    serialized_data  += b'END'
                    try:
                        conn.sendall(serialized_data)
                    except Exception as e:
                        print(e)
                    
                    DataReceived = conn.recv(1024)
                    API_Parameters.Peaks = np.array(pack.unpackb(DataReceived.strip(),  raw=False))
                    API_Parameters.PlotPeaks = True
                    try:
                        API_Parameters.PlotCalibrationSignal.signal.emit()
                    except Exception as e:
                        msgbox.alert(e)
                    serialized_data = pack.packb([1], use_bin_type=True)
                    try:
                        conn.sendall(serialized_data)
                    except Exception as e:
                        print(e)

                elif data == "PLOT /Detection":
                    serialized_data = pack.packb([1], use_bin_type=True)
                    serialized_data  += b'END'
                    try:
                        conn.sendall(serialized_data)
                    except Exception as e:
                        print(e)
                    data = b''
                    while True:
                        try:
                            chunk = conn.recv(1024)
                            if b'END' in chunk:
                                chunk = chunk[:-3]
                                data += chunk
                                break
                            else:
                                data += chunk
                        except Exception as e:
                            msgbox.alert(e)
                            break
                    try:
                        API_Parameters.SynergiesModels = pack.unpackb(data, max_array_len = len(data), raw=False)
                    except Exception as e:
                        msgbox.alert(e)
                    API_Parameters.PlotModels = True
                    try:
                        API_Parameters.PlotCalibrationSignal.signal.emit()
                    except Exception as e:
                        msgbox.alert(e)
                    serialized_data = pack.packb([1], use_bin_type=True)
                    try:
                        conn.sendall(serialized_data)
                    except Exception as e:
                        print(e)                   
                
                elif data == "UPLOAD /Configurations":
                    try:
                        Thresholds, Peaks, AnglesOutput, SynergyBase = API_Parameters.UploadCalibrationFromJson()
                        API_Parameters.Thresholds = Thresholds
                        API_Parameters.Peaks = Peaks
                        API_Parameters.AnglesOutput = AnglesOutput
                        API_Parameters.SynergyBase = SynergyBase
                        API_Parameters.SynergiesNumber = len(AnglesOutput)
                    except Exception as e:
                        msgbox.alert(e)                    
                    
                    serialized_data = pack.packb([1], use_bin_type = True)
                    serialized_data  += b'END'
                    
                    try:
                        conn.sendall(serialized_data)
                    except Exception as e:
                        msgbox.alert(e)
                    
                    API_Parameters.PlotUploadedConfig = True
                    API_Parameters.PlotCalibrationSignal.signal.emit()
                    API_Parameters.CalibrationStageFinished = True

                elif data == "GET /JsonConfiguration":
                    dictionary = {"Thresholds": API_Parameters.Thresholds,
                                  "Peaks": API_Parameters.Peaks,
                                   "synergy_CursorMap": API_Parameters.AnglesOutput,
                                   "SynergyBase": API_Parameters.SynergyBase}
                    serialized_data = pack.packb(dictionary, use_bin_type = True)  
                    serialized_data  += b'END' 
                    try:
                        conn.sendall(serialized_data)
                    except Exception as e:
                        msgbox.alert(e)

                elif data == "GET /ExperimentTimestamp":
                    serialized_data = pack.packb(API_Parameters.ExperimentTimestamp, use_bin_type = True)
                    serialized_data  += b'END' 
                    try:
                        conn.sendall(serialized_data)
                    except Exception as e:
                        msgbox.alert(e)
                                      

                else:
                   print("Invalid request", data)
                   pass
