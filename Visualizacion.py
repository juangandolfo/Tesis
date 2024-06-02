import Visualization_parameters as params
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.gridspec as GridSpec
import matplotlib.widgets as widgets
import socket
import threading
import json
import time
#import pymsgbox as msgbox
from multiprocessing import Process


# TCP/IP visualization client ------------------------------------------------------------------------------
HOST = "127.0.0.1"  # The server's hostname or IP address
PORT_Client = 6002  # The port used by the API server

# Create a socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def Connect():
    notConnected = True
    while notConnected:
        try:
            client_socket.connect((HOST, PORT_Client))
            notConnected = False
        except Exception as e:
            #print(e)
            pass
#-----------------------------------------------------------------------------------------------------------

# Function to send the request and receive the data from MP
def Request(type):
    start = time.time()
    request = "GET /" + type
    try:
        try:
            client_socket.sendall(request.encode())
        except Exception as e:
            print(e)
    except socket.error as e:
        print(e)

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
    #print("Time elapsed: ", end - start)

    serialized_data = data.decode().rstrip("~") # Quit the delimiter and decode the received data
    response_data = json.loads(serialized_data) # Get the original data

    if response_data == []:
        raise Exception("PM:No data received")
    return response_data

# Semaphore to lock the stack
MusclesStackSemaphore = threading.Semaphore(1)
SinergiesStackSemaphore = threading.Semaphore(1)

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

class Visualization:
    def Initialize(self):
        # Request parameters
        Parameters = Request("Parameters")
        params.MusclesNumber = int(Parameters[0])
        params.SynergiesNumber = int(Parameters[1])
        params.SampleRate = Parameters[2]
        params.Pts2Display = round(params.Time2Display * params.SampleRate)
        params.TimeStep = 1 / params.SampleRate
        
        self.ShowMuscle = [True for _ in range(params.MusclesNumber)]
        self.ShowSynergy = [True for _ in range(params.SynergiesNumber)]
        # Create the figure and axis objects
        self.fig = plt.figure()
        gs = GridSpec.GridSpec(nrows=3, ncols=3, width_ratios=[3, 3, 1], height_ratios=[3, 1, 3])

        # Add a menu to the plot          
        MusclesMenuSpace = plt.axes([0.8, 0.55, 0.15, 0.4])
        MusclesListForMenu = [f'Muscle {i+1}' for i in range(params.MusclesNumber)]
        self.MusclesMenu = widgets.CheckButtons(MusclesMenuSpace, MusclesListForMenu, [True for _ in range(params.MusclesNumber)])
        self.MusclesMenu.on_clicked(self.MusclesMenu_CallBack)

        SynergiesMenuSpace = plt.axes([0.8, 0.05, 0.15, 0.4])
        SynergiesListForMenu = [f'Synergy {i+1}' for i in range(params.SynergiesNumber)]
        self.SynergiesMenu = widgets.CheckButtons(SynergiesMenuSpace, SynergiesListForMenu, [True for _ in range(params.SynergiesNumber)])
        self.SynergiesMenu.on_clicked(self.SynergiesMenu_CallBack)

        #configure muscles plot
        self.DotsMuscles = self.fig.add_subplot(gs[0, 0])
        self.DotsMuscles.set_xlabel('Muscles')
        self.DotsMuscles.set_ylabel('Activation')
        self.DotsMuscles.set_title('Last 5 seconds of muscle activation')
        self.DotsMuscles.legend()

        #conself.figure synergies plot
        self.DotsSynergies = self.fig.add_subplot(gs[2, 0])
        self.DotsSynergies.set_xlabel('synergies')
        self.DotsSynergies.set_ylabel('Activation')
        self.DotsSynergies.set_title('Last 5 seconds of synergies activation')
        self.DotsSynergies.legend()

        BarsMusculos = self.fig.add_subplot(gs[0, 1])
        BarsMusculos.set_xticks(np.linspace(0, params.MusclesNumber-1, params.MusclesNumber))
        musclesList = ['Muscle {}'.format(i+1) for i in range(params.MusclesNumber)]
        BarsMusculos.set_xticklabels(musclesList)
        BarsMusculos.set_xlabel('Muscles')
        BarsMusculos.set_ylabel('Activation')
        BarsMusculos.set_title('Muscle Activation')
        for tick in BarsMusculos.get_xticklabels():
            tick.set_rotation(30)

        BarsSynergies = self.fig.add_subplot(gs[2, 1])
        BarsSynergies.set_xticks(np.linspace(0, params.SynergiesNumber-1, params.SynergiesNumber))
        synergiesList = ['Synergy {}'.format(i+1) for i in range(params.SynergiesNumber)]
        BarsSynergies.set_xticklabels(synergiesList)
        BarsSynergies.set_xlabel('Synergies')
        BarsSynergies.set_ylabel('Activation')
        BarsSynergies.set_title('Synergies Activation')
        for tick in BarsSynergies.get_xticklabels():
            tick.set_rotation(30)


        self.DotsMuscles.set_ylim([0, 0.5])
        self.DotsSynergies.set_ylim([0, 0.5])
        BarsMusculos.set_ylim([0, 0.5])
        BarsSynergies.set_ylim([0, 0.5])

        # Create empty buffers
        self.MusclesBuffer = Buffer(params.MusclesNumber, params.Pts2Display)
        self.SynergiesBuffer = Buffer(params.MusclesNumber, params.Pts2Display)
        self.x = Buffer(params.Pts2Display, 1)
        #self.x.Buffer = np.linspace((params.current_x - params.Pts2Display)/params.SampleRate, params.current_x/params.SampleRate, params.Pts2Display)
        self.x.Buffer = np.linspace(params.current_x - params.Time2Display, params.current_x, params.Pts2Display)
        self.MusclesLines = []
        for i in range(params.MusclesNumber):
            line, = self.DotsMuscles.plot(self.x.Buffer, self.MusclesBuffer.Buffer[:, i], color=params.MusclesColors[i])
            self.MusclesLines.append(line)
        self.SynergiesLines = []
        for i in range(params.MusclesNumber):
            line, = self.DotsSynergies.plot(self.x.Buffer, self.SynergiesBuffer.Buffer[:, i], color=params.SynergiesColors[i])
            self.SynergiesLines.append(line)

        self.bar1 = BarsMusculos.bar(range(params.MusclesNumber),range(params.MusclesNumber))
        self.bar2 = BarsSynergies.bar(range(params.SynergiesNumber),range(params.SynergiesNumber))

    # Update function for FuncAnimation

    def MusclesMenu_CallBack(self, label):
        self.ShowMuscle = self.MusclesMenu.get_status()
        
    def SynergiesMenu_CallBack(self, label):
        self.ShowSynergy = self.SynergiesMenu.get_status()
        

    def update(self,frame):
        print(params.current_x)

        try:
            MusclesActivation = Request("Muscles")
            MusclesStackSemaphore.acquire()
            self.MusclesBuffer.add_matrix(MusclesActivation)
            MusclesStackSemaphore.release()
              # in the next line i will update the bar plot
            for bar, line in zip(self.bar1, MusclesActivation[-1]):
                bar.set_height(line)
            for line in MusclesActivation:
                params.current_x += params.TimeStep
                self.x.add_point(params.current_x)
        except Exception as e:
            print(e)

        try:
            SynergiesActivation = Request("Synergies")
            SinergiesStackSemaphore.acquire()
            self.SynergiesBuffer.add_matrix(SynergiesActivation)
            SinergiesStackSemaphore.release()
            for bar, line in zip(self.bar2, SynergiesActivation[-1]):
                bar.set_height(line)
        except Exception as e:
            print(e)

        for line in self.MusclesLines:
            if self.ShowMuscle[self.MusclesLines.index(line)] == True:
                line.set_data(self.x.Buffer, self.MusclesBuffer.Buffer[:, self.MusclesLines.index(line)])
            else:
                line.set_data(self.x.Buffer, np.zeros(params.Pts2Display))
        
        for line in self.SynergiesLines:
            if self.ShowSynergy[self.SynergiesLines.index(line)] == True:
                line.set_data(self.x.Buffer, self.SynergiesBuffer.Buffer[:, self.SynergiesLines.index(line)])
            else:
                line.set_data(self.x.Buffer, np.zeros(params.Pts2Display))

        self.DotsMuscles.set_xlim([params.current_x - params.Time2Display, params.current_x])
        self.DotsSynergies.set_xlim([params.current_x - params.Time2Display, params.current_x])

def RunAnimation():
    Connect()
    vis = Visualization()
    vis.Initialize()
    # Create FuncAnimation instance
    ani = animation.FuncAnimation(vis.fig, vis.update, interval=1,cache_frame_data= False) #/params.update_freq
    # Show the plot
    plt.show()
    

Animation_Process = Process(target=RunAnimation)
