import Visualization_parameters as params
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.gridspec as GridSpec
import matplotlib.widgets as widgets
import socket
import threading
import json
from multiprocessing import Process
import msgpack as pack
import pymsgbox as msgbox
import time

LastChunk = b''




# PARAMETERS -----------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------
HOST = "127.0.0.1"  # The server's hostname or IP address
PORT_Client = 6002  # The port used by the API server

# TCP/IP visualization client ------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
vacio = pack.packb([], use_bin_type = True)
#-----------------------------------------------------------------------------------------------------------
def Connect():
    global client_socket
    notConnected = True
    while notConnected:
        try:
            client_socket.connect((HOST, PORT_Client))
            notConnected = False
        except Exception as e:
            msgbox.alert(f'Connect: {e}')

def CloseConnection():
    global client_socket
    client_socket.close()
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#-----------------------------------------------------------------------------------------------------------
def Request(type):
    global LastChunk
    with Socket_Lock:
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
    
    

# CLASSES --------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------
class Buffer:
    def __init__(self, MusclesNumber, Pts2Display):
        self.Buffer = np.zeros((Pts2Display, MusclesNumber))
        self.reconnect_successful = True

    def add_point(self, data):
        self.Buffer = np.roll(self.Buffer, -1, axis=0)
        self.Buffer[-1] = data
        return self.Buffer

    def add_matrix(self, data):
        for line in data:
            self.add_point(line)

#-----------------------------------------------------------------------------------------------------------
class Visualization:
    def Initialize(self):
        # SET THE PARAMETERS INITIAL VALUES
        self.connection_lost = False
        self.reconnect_successful = True
        try:
            Parameters = Request("Parameters")
        except Exception as e:
            msgbox.alert(e)
        params.MusclesNumber = int(Parameters[0])
        params.SynergiesNumber = int(Parameters[1])
        params.SampleRate = Parameters[2]
        params.Pts2Display = round(params.Time2Display * params.SampleRate)
        params.TimeStep = 1 / params.SampleRate

        self.ShowMuscle = [True for _ in range(params.MusclesNumber)]
        self.ShowSynergy = [True for _ in range(params.SynergiesNumber)]
        

        # CREATE THE FIGURE AND AXIS OBJECTS
        self.fig = plt.figure()
        gs = GridSpec.GridSpec(nrows=3, ncols=3, width_ratios=[3, 3, 1], height_ratios=[3, 1, 3])


        # ADD A MENU TO THE PLOT
        # Create the Muscles checkboxes
        MusclesMenuSpace = plt.axes([0.8, 0.55, 0.15, 0.4])
        MusclesListForMenu = [f'Muscle {i+1}' for i in range(params.MusclesNumber)]
        self.MusclesMenu = widgets.CheckButtons(MusclesMenuSpace, MusclesListForMenu, [True for _ in range(params.MusclesNumber)])
        self.MusclesMenu.on_clicked(self.MusclesMenu_CallBack)

        # Create the Synergies checkboxes
        SynergiesMenuSpace = plt.axes([0.8, 0.05, 0.15, 0.4])
        SynergiesListForMenu = [f'Synergy {i+1}' for i in range(params.SynergiesNumber)]
        self.SynergiesMenu = widgets.CheckButtons(SynergiesMenuSpace, SynergiesListForMenu, [True for _ in range(params.SynergiesNumber)])
        self.SynergiesMenu.on_clicked(self.SynergiesMenu_CallBack)


        # CREATE THE PLOTS
        # Create the Muscles plot
        self.DotsMuscles = self.fig.add_subplot(gs[0, 0])
        self.DotsMuscles.set_xlabel('Muscles')
        self.DotsMuscles.set_ylabel('Activation')
        self.DotsMuscles.set_title('Last 5 seconds of muscle activation')
        self.DotsMuscles.legend()
        
        # Create the Synergies plot
        self.DotsSynergies = self.fig.add_subplot(gs[2, 0])
        self.DotsSynergies.set_xlabel('synergies')
        self.DotsSynergies.set_ylabel('Activation')
        self.DotsSynergies.set_title('Last 5 seconds of synergies activation')
        self.DotsSynergies.legend()


        # CREATE THE BARS PLOTS
        # Create the Muscles bar plot
        BarsMusculos = self.fig.add_subplot(gs[0, 1])
        BarsMusculos.set_xticks(np.linspace(0, params.MusclesNumber-1, params.MusclesNumber))
        musclesList = ['Muscle {}'.format(i+1) for i in range(params.MusclesNumber)]
        BarsMusculos.set_xticklabels(musclesList)
        BarsMusculos.set_xlabel('Muscles')
        BarsMusculos.set_ylabel('Activation')
        BarsMusculos.set_title('Muscle Activation')
        for tick in BarsMusculos.get_xticklabels():
            tick.set_rotation(30)

        # Create the Synergies bar plot
        BarsSynergies = self.fig.add_subplot(gs[2, 1])
        BarsSynergies.set_xticks(np.linspace(0, params.SynergiesNumber-1, params.SynergiesNumber))
        synergiesList = ['Synergy {}'.format(i+1) for i in range(params.SynergiesNumber)]
        BarsSynergies.set_xticklabels(synergiesList)
        BarsSynergies.set_xlabel('Synergies')
        BarsSynergies.set_ylabel('Activation')
        BarsSynergies.set_title('Synergies Activation')
        for tick in BarsSynergies.get_xticklabels():
            tick.set_rotation(30)


        # SET THE LIMITS OF THE PLOTS
        # Set between 0 and 1 as data is normalized
        self.DotsMuscles.set_ylim([0, 1])
        self.DotsSynergies.set_ylim([0, 1])
        BarsMusculos.set_ylim([0, 1])
        BarsSynergies.set_ylim([0, 1])


        # CREATE THE BUFFERS
        self.MusclesBuffer = Buffer(params.MusclesNumber, params.Pts2Display)
        self.SynergiesBuffer = Buffer(params.SynergiesNumber, params.Pts2Display)
        self.x = Buffer(params.Pts2Display, 1)
        self.x.Buffer = np.linspace(params.current_x - params.Time2Display, params.current_x, params.Pts2Display)

        self.muscles = self.MusclesBuffer.Buffer
        self.synergies = self.SynergiesBuffer.Buffer
        xBuffer = self.x.Buffer        

        # CREATE THE LINE OBJECTS
        # Muscles lines
        self.MusclesLines = []
        for i in range(params.MusclesNumber):
            line, = self.DotsMuscles.plot(self.x.Buffer, self.MusclesBuffer.Buffer[:, i], color=params.MusclesColors[i])
            self.MusclesLines.append(line)
        
        # Synergies lines
        self.SynergiesLines = []
        for i in range(params.SynergiesNumber):
            line, = self.DotsSynergies.plot(self.x.Buffer, self.SynergiesBuffer.Buffer[:, i], color=params.SynergiesColors[i])
            self.SynergiesLines.append(line)


        # CREATE THE BAR OBJECTS
        self.musclesBar = BarsMusculos.bar(range(params.MusclesNumber),range(params.MusclesNumber))
        self.synergiesBar = BarsSynergies.bar(range(params.SynergiesNumber),range(params.SynergiesNumber))
    

    # CALLBACK FUNCTIONS
    def MusclesMenu_CallBack(self, label):
        self.ShowMuscle = self.MusclesMenu.get_status()

    def SynergiesMenu_CallBack(self, label):
        self.ShowSynergy = self.SynergiesMenu.get_status()


    # UPDATE FUNCTION
    def update(self,frame):
        start = time.time()
        print(frame)
        try:
        
            # GET THE DATA FROM THE SERVER AND SAVE IT TO THE SHARED BUFFERS
            try:
                MusclesRequest = Request("Muscles")
            except Exception as e:
                MusclesRequest = []
                print(e)
            
            try:
                SynergiesRequest = Request("Synergies")
            except Exception as e:
                SynergiesRequest = []
                print(e)
            
            try:
                if MusclesStackSemaphore.acquire(blocking=False): 
                    self.MusclesBuffer.add_matrix(MusclesRequest)
                    self.muscles = self.MusclesBuffer.Buffer
                    MusclesStackSemaphore.release()
                else:
                    print("                                                             Muscle semaphore taken")
                
                if SinergiesStackSemaphore.acquire(blocking=False):
                    self.SynergiesBuffer.add_matrix(SynergiesRequest)
                    self.synergies = self.SynergiesBuffer.Buffer
                    SinergiesStackSemaphore.release()
                else:
                    print("                                                             synergies semaphore taken")
                
                
                if XSemaphore.acquire(blocking=False):
                    for line in MusclesRequest: 
                        params.current_x += params.TimeStep
                        self.x.add_point(params.current_x)
                    xBuffer = self.x.Buffer
                    XSemaphore.release()
                else:
                    print("                                                             X semaphore taken")
                

            except Exception as e:
                msgbox.alert(f'Semaphores {e}')
            
            # UPDATE THE MUSCLES BAR
            MusclesActivation = self.muscles[-1]
            for bar, line in zip(self.musclesBar, MusclesActivation):
                bar.set_height(line)
                
            SynergiesActivation = self.synergies[-1]
            for bar, line in zip(self.synergiesBar, SynergiesActivation):
                bar.set_height(line)

            # UPDATE THE LINES PLOTS
            # Muscles lines
            for line in self.MusclesLines:
                if self.ShowMuscle[self.MusclesLines.index(line)] == True:
                    line.set_data(xBuffer, self.muscles[:, self.MusclesLines.index(line)])
                else:
                    line.set_data(xBuffer, np.zeros(params.Pts2Display))
            if params.current_x > self.DotsMuscles.get_xlim()[1]:
                self.DotsMuscles.set_xlim([params.current_x , params.current_x + params.Time2Display])

            # Synergies lines
            for line in self.SynergiesLines:
                if self.ShowSynergy[self.SynergiesLines.index(line)] == True:
                    line.set_data(xBuffer, self.synergies[:, self.SynergiesLines.index(line)])
                else:
                    line.set_data(xBuffer, np.zeros(params.Pts2Display))
            if params.current_x > self.DotsSynergies.get_xlim()[1]:
                self.DotsSynergies.set_xlim([params.current_x, params.current_x + params.Time2Display])

            # self.DotsSynergies.set_xlim([params.current_x - params.Time2Display, params.current_x])
           
        except Exception as e:
            msgbox.alert(f'Vis {e}')
        
        print((time.time() - start)*1000)

# INSTANCES ------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------
MusclesStackSemaphore = threading.Semaphore(1)
SinergiesStackSemaphore = threading.Semaphore(1)
RequestSemaphore = threading.Semaphore(1)
XSemaphore = threading.Semaphore(1)
Socket_Lock = threading.Lock()

# FUNCTIONS ------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------

# MAIN LOOP ------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------

def RunAnimation():
    Connect()
    vis = Visualization()
    vis.Initialize()
    ani = animation.FuncAnimation(vis.fig, vis.update,frames = 500, interval = 50, repeat = True, cache_frame_data=False)
    plt.show()

if __name__ == '__main__':
    Animation_Process = Process(target=RunAnimation)
    Animation_Process.start()
