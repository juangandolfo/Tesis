import time
import threading
#import random
import numpy as np
from functools import partial

class Sensor(threading.Thread):
    def __init__(self, callbackFunc, running):
        threading.Thread.__init__(self) # Initialize the threading superclass
        self.MusclesActivations = 0 
        self.SynergiesActivations = 0 
        self.running = running # Store the current state of the Flag
        self.callbackFunc = callbackFunc # Store the callback function
        
        self.MusclesNumber = 8
        self.SynergiesNumber = 8

    def run(self):
        while self.running.is_set(): # Continue grabbing data from sensor while Flag is set
            time.sleep(0.10)  # Time to sleep in seconds, emulating some sensor process taking time
            self.MusclesActivations = np.random.random((np.random.randint(100,200),self.MusclesNumber))*0.01 # Generate random integers to emulate data from sensor
            self.SynergiesActivations = np.random.random((np.random.randint(100,200),self.SynergiesNumber))*0.01 # Generate random integers to emulate data from sensor
            self.callbackFunc.doc.add_next_tick_callback(partial(self.callbackFunc.update, self.MusclesActivations,self.SynergiesActivations)) # Call Bokeh webVisual to inform that new data is available
        print("Sensor thread killed") # Print to indicate that the thread has ended