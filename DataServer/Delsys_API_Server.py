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
import DataServer.API_Parameters as params

HOST = "127.0.0.1"  # Standard adress (localhost)
PORT = 6001  # Port to listen on (non-privileged ports are > 1023)


def DictionaryToMatrix(formatted_dictionary, emgPositionVector):
    python_dictionary = {}
    #outArr = [[] for i in range(len(formatted_dictionary.Keys))] # matrix
    keys = []
    
    # for i in formatted_dictionary.Keys:
    #     keys.append(i)
    # '''for j in range(len(keys)):
    #     # outArr[j].append(np.asarray(formatted_dictionary[keys[j]], dtype='object'))
    #     # full data
    # '''
    # DataRows = min(set([len(formatted_dictionary[keys[i]]) for i in emgPositionVector]))
    # DataColumns = len(emgPositionVector)
    # OutMatrix = np.zeros((DataRows,DataColumns))
    # for j in range(len(emgPositionVector)):
    #     OutMatrix[:,j] = np.asarray(formatted_dictionary[keys[emgPositionVector[j]]])[:DataRows]

    DataRows = min(set([len(formatted_dictionary[ID]) for ID in params.Channels_ID]))
    DataColumns = len(params.Channels_ID)
    OutMatrix = np.zeros((DataRows,DataColumns))
    for j in range(len(params.Channels_ID)):
        OutMatrix[:,j] = np.asarray(formatted_dictionary[params.Channels_ID[j]])[:DataRows]

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
            params.CreateExperimentName()
            while True:
                #print("                                                 API Server live")
                try:
                    s.settimeout(600)
                    DataReceived = conn.recv(1024)
                except Exception as e:
                    print("API1", e)
                data = DataReceived.decode().strip()
                #print(data)
              
                if data == "GET /data":
                    dataReady = AeroInstance.CheckDataQueue()
                    if dataReady:
                        try:
                            response_data = DictionaryToMatrix(AeroInstance.PollData(),emgPositionVector)
                            #print(response_data)
                        except Exception as e:
                            print(f"Poll Data: {e}, {response_data}")
                    else:
                        response_data=[]
                    serialized_data = pack.packb(response_data,use_bin_type=True) # Serialize the object using msgpack

                    if params.TerminateCalibrationFlag:
                        serialized_data  += b"TC" # Add a delimiter at the end
                        params.TerminateCalibrationFlag = False

                    elif params.CalibrationStageInitialized:
                            params.CalibrationStageInitialized = False

                            if params.CalibrationStage == 1:
                                try:
                                    serialized_data  += b"CS1" + str(params.selectedSensorIndex).encode() # Add a delimiter at the end
                                except Exception as e:
                                    msgbox.alert(f'[DAS-001] Error encoding calibration stage 1 sensor index: {e}')
                            elif params.CalibrationStage == 2:
                                serialized_data  += b"CS2" + str(params.selectedSensorIndex).encode() # Add a delimiter at the end
                            elif params.CalibrationStage == 3:
                                serialized_data  += b"CS3" # Add a delimiter at the end
                            elif params.CalibrationStage == 4:
                                serialized_data  += b"CS4" # Add a delimiter at the end
                            elif params.CalibrationStage == 6:
                                serialized_data  += b"CS6" # Add a delimiter at the end

                    elif params.CalibrationStageFinished:
                        params.CalibrationStageFinished = False
                        serialized_data  += b"CSF" # Add a delimiter at the end

                    elif params.SimulationCalibration == True:
                        params.SimulationCalibration = False
                        serialized_data  += b"CS5" # Add a delimiter at the end

                    elif params.StartCalibration == True:
                        params.StartCalibration = False
                        serialized_data  += b"ICS" # Add a delimiter at the end
                        
                    else:
                        serialized_data += b'END' # Add a delimiter at the end
                        #print(serialized_data)
                    try:
                        conn.sendall(serialized_data)
                    except Exception as e:
                        print("API sending", e)

                elif data == "GET /SensorsNumber":
                    serialized_data = pack.packb(params.ChannelsNumber, use_bin_type=True)
                    serialized_data  += b'END'
                    try:
                        conn.sendall(serialized_data)
                    except Exception as e:
                        print(e)
                    params.Initialize()
                    
                
                elif data == "GET /SensorStickers":
                    serialized_data = pack.packb(params.SensorStickers, use_bin_type=True)
                    serialized_data  += b'END'
                    try:
                        conn.sendall(serialized_data)
                    except Exception as e:
                        print(e)

                elif data == "GET /SampleRate":
                    serialized_data = pack.packb(params.SampleRate, use_bin_type=True)
                    serialized_data  += b'END'
                    try:
                        conn.sendall(serialized_data)
                    except Exception as e:
                        print(e)

                elif data == "GET /CalibrationTime":
                    serialized_data = pack.packb(params.TimeCalibStage3, use_bin_type=True)
                    serialized_data  += b'END'
                    try:
                        conn.sendall(serialized_data)
                    except Exception as e:
                        print(e)

                elif data == "GET /Angles":
                    params.AnglesOutputSemaphore.acquire()
                    serialized_data = pack.packb(params.AnglesOutput, use_bin_type=True)
                    params.AnglesOutputSemaphore.release()
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
                        msgbox.alert(f'[DAS-002] Error packing threshold plot response: {e}')
                    serialized_data  += b'END'
                    try:
                        conn.sendall(serialized_data)
                    except Exception as e:
                        print(e)
                    
                    data = conn.recv(1024)
                    # params.Thresholds = np.array(pack.unpackb(data.strip(), raw=False))
                    params.Thresholds = list(map(float, pack.unpackb(data.strip(), raw=False)))
                    params.PlotThresholds = True
                    try:
                        params.PlotCalibrationSignal.signal.emit()
                    except Exception as e:
                        msgbox.alert(f'[DAS-003] Error emitting threshold plot calibration signal: {e}')
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
                    # params.Peaks = np.array(pack.unpackb(DataReceived.strip(),  raw=False))
                    # params.Peaks = pack.unpackb(DataReceived.strip(), raw=False)
                    params.Peaks = list(map(float, pack.unpackb(DataReceived.strip(), raw=False)))
                    params.PlotPeaks = True
                    try:
                        params.PlotCalibrationSignal.signal.emit()
                    except Exception as e:
                        msgbox.alert(f'[DAS-004] Error emitting peaks plot calibration signal: {e}')
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
                            msgbox.alert(f'[DAS-005] Error receiving detection data chunk: {e}')
                            break
                    try:
                        params.SynergiesModels = pack.unpackb(data, max_array_len = len(data), raw=False)
                    except Exception as e:
                        msgbox.alert(f'[DAS-006] Error unpacking synergies models data: {e}')
                    params.PlotModels = True
                    try:
                        params.PlotCalibrationSignal.signal.emit()
                    except Exception as e:
                        msgbox.alert(f'[DAS-007] Error emitting detection plot calibration signal: {e}')
                    serialized_data = pack.packb([1], use_bin_type=True)
                    try:
                        conn.sendall(serialized_data)
                    except Exception as e:
                        print(e)                   
                
                elif data == "UPLOAD /Configurations":
                    try:
                        Thresholds, Peaks, AnglesOutput, SynergyBase, SensorStickers = params.UploadCalibrationFromJson()
                        # Chequeo si cada uno es null, si no es mnull lo asigno y si es null vemos que hacemos 
                        if Thresholds is not None:
                            params.Thresholds = Thresholds
                        if Peaks is not None:
                            params.Peaks = Peaks
                        if AnglesOutput is not None:
                            params.AnglesOutput = AnglesOutput
                        if SynergyBase is not None:
                            params.SynergyBase = SynergyBase
                        if SensorStickers is not None:
                            params.SensorStickers = SensorStickers
                        params.SynergiesNumber = len(AnglesOutput)
                    except Exception as e:
                        msgbox.alert(f'[DAS-008] Error uploading configuration from JSON: {e}')                    
                    
                    serialized_data = pack.packb([1], use_bin_type = True)
                    serialized_data  += b'END'
                    
                    try:
                        conn.sendall(serialized_data)
                    except Exception as e:
                        msgbox.alert(f'[DAS-009] Error sending configuration upload response: {e}')
                    
                    params.PlotUploadedConfig = True
                    params.PlotCalibrationSignal.signal.emit()
                    params.CalibrationStageFinished = True

                elif data == "UPLOAD /Projections":
                    try:
                        Thresholds, Peaks, AnglesOutput, SynergyBase, SensorStickers = params.UploadCalibrationFromJson()
                        params.AnglesOutput = AnglesOutput
                        params.SynergyBase = SynergyBase
                        params.SynergiesNumber = len(AnglesOutput)
                    except Exception as e:
                        msgbox.alert(f'[DAS-010] Error uploading projections from JSON: {e}')
                    
                    serialized_data = pack.packb([1], use_bin_type = True)
                    serialized_data  += b'END'
                    
                    try:
                        conn.sendall(serialized_data)
                    except Exception as e:
                        msgbox.alert(f'[DAS-011] Error sending projections upload response: {e}')
                    
                    params.PlotUploadedConfig = True
                    params.PlotCalibrationSignal.signal.emit()
                    params.CalibrationStageFinished = True

                elif data == "GET /JsonConfiguration":
                    # i need to make sure the format of thresholds and peaks is not numpy
                    try:
                        dictionary = {"Thresholds": params.Thresholds,
                                    "Peaks": params.Peaks,
                                    "synergy_CursorMap": params.AnglesOutput,
                                    "SynergyBase": params.SynergyBase,
                                    "SensorStickers": params.SensorStickers}
                        print(dictionary)
                        serialized_data = pack.packb(dictionary, use_bin_type = True)  
                        serialized_data  += b'END' 
                        try:
                            conn.sendall(serialized_data)
                        except Exception as e:
                            msgbox.alert(f'[DAS-012] Error sending JSON configuration response: {e}')
                    except Exception as e:
                        msgbox.alert(f'[DAS-013] Error processing JSON configuration request: {e}') 

                elif data == "GET /ExperimentTimestamp":
                    serialized_data = pack.packb(params.ExperimentTimestamp, use_bin_type = True)
                    serialized_data  += b'END' 
                    try:
                        conn.sendall(serialized_data)
                    except Exception as e:
                        msgbox.alert(f'[DAS-014] Error sending experiment timestamp response: {e}')

                elif data == "GET /Ping":
                    serialized_data = pack.packb([1,time.time()], use_bin_type = True)
                    serialized_data  += b'END' 
                    try:
                        conn.sendall(serialized_data)
                    except Exception as e:
                        msgbox.alert(f'[DAS-015] Error sending ping response: {e}')

                else:
                   print("Invalid request", data)
                   pass
