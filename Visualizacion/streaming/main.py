from Visual import *
from Sensor import *
import VisualizationParameters as params

def threads(callbackFunc, running):
    # Set multiple threads
    sensor = Sensor(callbackFunc=callbackFunc, running=running) # Instantiate the Sensor thread
    # Start threads 
    sensor.start() # Run the thread to start collecting data

def main():

    #Set global flag
    Connect()
    parameters = Request('Parameters')
    event = threading.Event() # Create an event to communicate between threads
    event.set() # Set the event to True
    
    params.MusclesNumber = int(parameters[0])
    params.SynergiesNumber = int(parameters[1])
    params.SampleRate = parameters[2]

    webVisual = Visual(callbackFunc=threads, running=event) # Instantiate a Bokeh web document
    threads(callbackFunc=webVisual, running=event) # Call Sensor thread

# Run command:
# bokeh serve --show streaming
main()