import time
import threading
#import random
import numpy as np
from functools import partial
import pymsgbox as msgbox
import msgpack as pack
import socket
import pandas as pd

# PARAMETERS -----------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------
HOST = "127.0.0.1"  # The server's hostname or IP address
PORT_Client = 6002  # The port used by the API server

# TCP/IP visualization client ------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#-----------------------------------------------------------------------------------------------------------
def Connect():
    global client_socket
    notConnected = True
    while notConnected:
        try:
            client_socket.connect((HOST, PORT_Client))
            notConnected = False
        except Exception as e:
            print(f'Connect: {e}')

def CloseConnection():
    global client_socket
    client_socket.close()
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#-----------------------------------------------------------------------------------------------------------
data = b''
chunk = b''
response_data = b''
vacio = pack.packb(b'\x90', use_bin_type = True)


def Request(type):
    global LastChunk
    global data
    global chunk
    global vacio
    global response_data
    
    response_data = []
    # Function to send a request and receive the data from the server
    request = "GET /" + type
    # client_socket.settimeout(3)
    data = b''
    try:
        client_socket.sendall(request.encode())
    except (socket.timeout, socket.error) as e:
        msgbox.alert(f"Communication error: {e}")
        # client_socket.close() #Close TCP/IP connection
    except Exception as e:
        print("PM request:", e)
    
    while True:
        try:
            chunk = client_socket.recv(1024)
            if b'END' in chunk:
                lastchunk = chunk
                chunk = chunk[:-3]
                data += chunk
                break  # Delimiter found
            else:
                data += chunk
        except Exception as e:
            msgbox.alert(f'Chunks fail {e}')
            msgbox.alert(data)
        
            try:
                # client_socket
                CloseConnection()
                msgbox.alert("Re-opening connection")
                Connect()
            except:
                msgbox.alert("connection rejected")

    try:
        if data == vacio: 
            raise Exception("Vis:No data received")
        else:
            response_data = pack.unpackb(data, max_array_len = len(data), raw=False)
            
    except Exception as e:
        if data != b'\x90':
            raise Exception(f'Cannot unpack data {data}')
    return response_data
# ---------------------------------------------------------------------------------------------------------------------------------

class Sensor(threading.Thread):
    def __init__(self, callbackFunc, running):
        threading.Thread.__init__(self) # Initialize the threading superclass
        #Connect()
        self.MusclesActivations = []
        self.SynergiesActivations = [] 
        self.running = running # Store the current state of the Flag
        self.callbackFunc = callbackFunc # Store the callback function
        
        self.pingRequested = False
        self.pingtime = []
       
    def run(self):
        counter = 0
        while self.running.is_set(): # Continue grabbing data from sensor while Flag is set
            start = time.time()
            time.sleep(0.016)  # Time to sleep in seconds, emulating some sensor process taking time
            self.MusclesActivations = Request('Muscles')
            self.SynergiesActivations = Request('Synergies')

            # Ping implementation to measure the comms latency 
            # if self.pingRequested == True:
            #     response = Request('PingUpdate')
            #     if response[0] == 1:
            #         self.pingtime.append(time.time() - response[1])
            #         counter += 1
            #         self.pingRequested = False
            #         print(f'Ping: {self.pingtime}')
            # else:
            #     PingRequest = time.time()
            #     response = Request('Ping')
            #     if response[0] == 1:
            #         self.pingRequested = True
            
            # if counter>1000:
            #     try:
            #         frame = pd.DataFrame(self.pingtime).to_csv('./PingTimes_Ej2.csv')
            #         # Save the DataFrame to a CSV file
            #         counter = 0
            #         self.pingtime = []
            #         msgbox.alert('Ping times saved')
            #     except Exception as e:
            #         msgbox.alert(e)
                
            self.callbackFunc.doc.add_next_tick_callback(partial(self.callbackFunc.update, self.MusclesActivations,self.SynergiesActivations)) # Call Bokeh webVisual to inform that new data is available
        print("Sensor thread killed") # Print to indicate that the thread has ended