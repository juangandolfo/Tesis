import Visualization_parameters as params
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.gridspec as GridSpec
import socket
import threading
import json
import time


# TCP/IP visualization client ------------------------------------------------------------------------------
HOST = "127.0.0.1"  # The server's hostname or IP address
PORT_Client = 6002  # The port used by the API server

# Create a socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT_Client))
#-----------------------------------------------------------------------------------------------------------

# Function to send the request and receive the data from MP
def Request(type):
    start = time.time()
    request = "GET /" + type
    client_socket.sendall(request.encode())
    
    data = b''       
    while True:
        try:
            #client_socket.settimeout(0.5)
            chunk = client_socket.recv(1024)
            data += chunk
            if b"~" in data:
                #print("Delimiter found")
                break  # Delimiter found
        except socket.timeout as e:
            print(e)
            continue
        except socket.error as e:
            print(e)
            continue
    end = time.time()
    print("Time elapsed: ", end - start)

    serialized_data = data.decode().rstrip("~") # Quit the delimiter and decode the received data
    response_data = json.loads(serialized_data) # Get the original data 
     
    if response_data == []:
        raise Exception("PM:No data received")
    return response_data

# Semaphore to lock the stack
stack_lock = threading.Semaphore(1)

class Buffer:
    def __init__(self, MusclesNumber, Pts2Display):
        self.Buffer = np.zeros((Pts2Display, MusclesNumber))
    
    def add_point(self, data):
        self.Buffer = np.roll(self.Buffer, -1, axis=0) # Roll the buffer to make space for the new vector
        self.Buffer[-1] = data
        return self.Buffer
    
    def add_matrix(self, data):
        for line in data:
            self.add_point(line)

# Request parameters
Parameters = Request("Parameters")
params.MusclesNumber = Parameters[0]
params.SynergiesNumber = Parameters[1]

# Create the figure and axis objects
fig = plt.figure()
gs = GridSpec.GridSpec(nrows=3, ncols=2, width_ratios=[1, 1], height_ratios=[3, 1, 3])

ax = fig.add_subplot(gs[0, 0])
bx = fig.add_subplot(gs[2, 0])
cx = fig.add_subplot(gs[0, 1])
dx = fig.add_subplot(gs[2, 1])

ax.set_ylim([0, 2])
bx.set_ylim([0, 2])
cx.set_ylim([0, 2])
dx.set_ylim([0, 2])

# Create empty buffers
MusclesBuffer = Buffer(params.MusclesNumber, params.Pts2Display)
SynergiesBuffer = Buffer(params.MusclesNumber, params.Pts2Display)
x = Buffer(params.Pts2Display, 1)
x.Buffer = np.linspace(params.current_x - params.Pts2Display, params.current_x, params.Pts2Display)
MusclesLines = []
for i in range(params.MusclesNumber):
    line, = ax.plot(x.Buffer, MusclesBuffer.Buffer[:, i], color=params.MusclesColors[i])
    MusclesLines.append(line)
SynergiesLines = []
for i in range(params.MusclesNumber):
    line, = bx.plot(x.Buffer, MusclesBuffer.Buffer[:, i], color=params.SynergiesColors[i])
    SynergiesLines.append(line)

bar1 = cx.bar(range(params.MusclesNumber),range(params.MusclesNumber))
bar2 = dx.bar(range(params.MusclesNumber),range(params.MusclesNumber))

# Update function for FuncAnimation
def update(frame):
    print(params.current_x)
    global MusclesBuffer

    MusclesActivation = Request("Muscles")
    #SynergiesActivation = Request("Synergies")
    
    stack_lock.acquire()
    MusclesBuffer.add_matrix(MusclesActivation)
    stack_lock.release()

    for line in MusclesLines:
        line.set_data(x.Buffer, MusclesBuffer.Buffer[:, MusclesLines.index(line)])
    for line in SynergiesLines:
        #line.set_data(x.Buffer, MusclesBuffer.Buffer[:, SynergiesLines.index(line)])
        line.set_data(x.Buffer, SynergiesBuffer.Buffer[:, SynergiesLines.index(line)])

    ax.set_xlim([params.current_x- params.Pts2Display, params.current_x])
    bx.set_xlim([params.current_x- params.Pts2Display, params.current_x])
    
    # in the next line i will update the bar plot
    for bar, line in zip(bar1, MusclesActivation[-1]):
        bar.set_height(line)
    
    for bar, line in zip(bar2, MusclesActivation[-1]):
        bar.set_height(line)
    
    for line in MusclesActivation:
        params.current_x = params.current_x + 1 #len(MusclesActivation)
        x.add_point(params.current_x)

# Create FuncAnimation instance
ani = animation.FuncAnimation(fig, update, interval=1,cache_frame_data= False)#/update_freq)

# Show the plot
plt.show()
