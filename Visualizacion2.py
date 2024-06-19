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

# PARAMETERS -----------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------
HOST = "127.0.0.1"  # The server's hostname or IP address
PORT_Client = 6002  # The port used by the API server

# TCP/IP visualization client ------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#-----------------------------------------------------------------------------------------------------------
def Connect():
    notConnected = True
    while notConnected:
        try:
            client_socket.connect((HOST, PORT_Client))
            notConnected = False
        except Exception as e:
            print(e)

#-----------------------------------------------------------------------------------------------------------
def Request(type):
    # Function to send a request and receive the data from the server
    request = "GET /" + type
    client_socket.settimeout(3)
    try:
        client_socket.sendall(request.encode())
        data = b''
        while True:
            try:
                chunk = client_socket.recv(1024)
                data += chunk
                if b"~" in data:
                    break  # Delimiter found
            except socket.timeout as e:
                print(e)
                continue
            except socket.error as e:
                print(e)
                continue

        serialized_data = data.decode().rstrip("~") # Quit the delimiter and decode the received data
        response_data = json.loads(serialized_data) # Get the original data

        if response_data == []:
            raise Exception("PM:No data received")
        return response_data
    
    except (socket.timeout, socket.error) as e:
        print(f"Communication error: {e}")
        client_socket.close() #Close TCP/IP connection

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

        Parameters = Request("Parameters")
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
        # GET THE DATA FROM THE SERVER AND SAVE IT TO THE SHARED BUFFERS
        try:
            MusclesActivation = Request("Muscles")
            # This semaphore is put in place for a future implementation of a threading architecture 
            # were one thread asks for data and the other continuously updates the plot
            MusclesStackSemaphore.acquire() 
            self.MusclesBuffer.add_matrix(MusclesActivation)
            MusclesStackSemaphore.release()
            
            # This is to update the x axis, it is executed only once because all the lines share the same time frames
            for line in MusclesActivation: 
                params.current_x += params.TimeStep
                self.x.add_point(params.current_x)

            # UPDATE THE MUSCLES BAR
            for bar, line in zip(self.musclesBar, MusclesActivation[-1]):
                bar.set_height(line)
            
        except Exception as e:
            print(e)

        try:
            SynergiesActivation = Request("Synergies")
            SinergiesStackSemaphore.acquire()
            self.SynergiesBuffer.add_matrix(SynergiesActivation)
            SinergiesStackSemaphore.release()

            # UPDATE THE SYNERGIES BAR
            for bar, line in zip(self.synergiesBar, SynergiesActivation[-1]):
                bar.set_height(line)

        except Exception as e:
             print(e)

        # UPDATE THE LINES PLOTS
        # Muscles lines
        for line in self.MusclesLines:
            if self.ShowMuscle[self.MusclesLines.index(line)] == True:
                line.set_data(self.x.Buffer, self.MusclesBuffer.Buffer[:, self.MusclesLines.index(line)])
            else:
                line.set_data(self.x.Buffer, np.zeros(params.Pts2Display))
        self.DotsMuscles.set_xlim([params.current_x - params.Time2Display, params.current_x])

        # Synergies lines
        for line in self.SynergiesLines:
            if self.ShowSynergy[self.SynergiesLines.index(line)] == True:
                line.set_data(self.x.Buffer, self.SynergiesBuffer.Buffer[:, self.SynergiesLines.index(line)])
            else:
                line.set_data(self.x.Buffer, np.zeros(params.Pts2Display))
        self.DotsSynergies.set_xlim([params.current_x - params.Time2Display, params.current_x])

# INSTANCES ------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------
MusclesStackSemaphore = threading.Semaphore(1)
SinergiesStackSemaphore = threading.Semaphore(1)

# FUNCTIONS ------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------

# MAIN LOOP ------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------
def RunAnimation():
    Connect()
    vis = Visualization()
    vis.Initialize()
    ani = animation.FuncAnimation(vis.fig, vis.update, interval=1, cache_frame_data=False)
    plt.show()

if __name__ == '__main__':
    Animation_Process = Process(target=RunAnimation)
    Animation_Process.start()
