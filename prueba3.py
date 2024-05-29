import scipy.signal
import Visualization_parameters as params
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.gridspec as GridSpec
import socket
import threading
import json
import time
import scipy

class LPF:
    def __init__(self):
        self.a, self.b = scipy.signal.iirfilter(N = 2, Wn = [2*np.pi*0.00001,2*np.pi*0.01], ftype = 'butter',fs=2*np.pi*1) 
        self.signal = np.zeros((len(self.b),params.MusclesNumber))
        self.filtered_signal = np.zeros((len(self.a)-1,params.MusclesNumber))
        print(self.a)
        print(self.b)
        print(sum(self.a)+sum(self.b))   

    def lpf(self,signal):
        self.signal = np.roll(self.signal,1,axis=0)
        self.signal[0] = signal
        # for i in range(params.MusclesNumber):
        #     self.filtered_signal[:,i] = scipy.signal.lfilter(a =self.a, b = self.b, x= self.signal[:,i])
        y = np.dot(self.b,self.signal)
        y = y - np.dot(self.a[1:],self.filtered_signal)
        y = y/self.a[0]
        
        self.filtered_signal = np.roll(self.filtered_signal,1,axis=0)
        self.filtered_signal[0] = y
        return y

    #return scipy.signal.lfilter(a,b,signal)
lpf = LPF()

# Function to send the request and receive the data from MP
def Request(type,current_x):
    y = 10 * np.sin(current_x*2*np.pi/200) + 5* np.random.rand(params.MusclesNumber)
    return y

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

# Create the figure and axis objects
fig = plt.figure()
gs = GridSpec.GridSpec(nrows=3, ncols=2, width_ratios=[10, 1], height_ratios=[3, 1, 3])

#configure muscles plot
DotsMuscles = fig.add_subplot(gs[0, 0])
DotsMuscles.set_xlabel('Muscles')
DotsMuscles.set_ylabel('Activation')
DotsMuscles.set_title('Last 5 seconds of muscle activation')
DotsMuscles.legend() 

#configure synergies plot
DotsSynergies = fig.add_subplot(gs[2, 0])
DotsSynergies.set_xlabel('synergies')
DotsSynergies.set_ylabel('Activation')
DotsSynergies.set_title('Last 5 seconds of synergies activation')
DotsSynergies.legend()


DotsMuscles.set_ylim([-15, 15])
DotsSynergies.set_ylim([-15, 15])

MusclesBuffer = Buffer(params.MusclesNumber, params.Pts2Display)
SynergiesBuffer = Buffer(params.MusclesNumber, params.Pts2Display)
x = Buffer(params.Pts2Display, 1)
x.Buffer = np.linspace(params.current_x - params.Pts2Display, params.current_x, params.Pts2Display)
MusclesLines = []
for i in range(params.MusclesNumber):
    line, = DotsMuscles.plot(x.Buffer, MusclesBuffer.Buffer[:, i], color=params.MusclesColors[i])
    MusclesLines.append(line)
SynergiesLines = []
for i in range(params.MusclesNumber):
    line, = DotsSynergies.plot(x.Buffer, SynergiesBuffer.Buffer[:, i], color=params.SynergiesColors[i])
    SynergiesLines.append(line)


# Update function for FuncAnimation
def update(frame):
    
    global MusclesBuffer
    global SynergiesBuffer

    MusclesActivation = Request("Muscles",current_x= params.current_x)
    SynergiesActivation = lpf.lpf(MusclesActivation)

    MusclesStackSemaphore.acquire()
    MusclesBuffer.add_matrix(MusclesActivation)
    MusclesStackSemaphore.release()

    SinergiesStackSemaphore.acquire()
    SynergiesBuffer.add_matrix(SynergiesActivation)
    SinergiesStackSemaphore.release()

    for line in MusclesLines:
        line.set_data(x.Buffer, MusclesBuffer.Buffer[:, MusclesLines.index(line)])
    for line in SynergiesLines:
        line.set_data(x.Buffer, SynergiesBuffer.Buffer[:, SynergiesLines.index(line)])

    DotsMuscles.set_xlim([params.current_x- params.Pts2Display, params.current_x])
    DotsSynergies.set_xlim([params.current_x- params.Pts2Display, params.current_x])
   
    counter = 0
    for line in MusclesActivation:
        params.current_x = params.current_x + 1 #len(MusclesActivation)
        x.add_point(params.current_x)
        counter += 1


# Create FuncAnimation instance
ani = animation.FuncAnimation(fig, update, interval=1,cache_frame_data= False)#/update_freq)

# Show the plot
plt.show()