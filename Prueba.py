import numpy as np
import matplotlib.pyplot as plt
import time
import matplotlib.gridspec as GridSpec
import LocalCircularBuffer 


# Define the update frequency in Hz
update_freq = 80
# Define the number of points to display
Time2Display=10 #in seconds
definition=1/10
Pts2Display=round(Time2Display/definition)
print(Pts2Display)

#define the number of channels
n_channels=3
current_x=0
# Create the circular buffer objects
x = LocalCircularBuffer.CircularBuffer(Pts2Display)
y1= LocalCircularBuffer.CircularBuffer(Pts2Display)
y2= LocalCircularBuffer.CircularBuffer(Pts2Display) 
y3= LocalCircularBuffer.CircularBuffer(Pts2Display)
#y=[LocalCircularBuffer.CircularBuffer(Pts2Display) for i in range(n_channels)]

# Create the figure and axis objects
fig =  plt.figure()
gs=GridSpec.GridSpec(nrows=3, ncols=2, width_ratios=[1, 1],height_ratios=[3,1,3])


ax = fig.add_subplot(gs[0,0])
ax.set_ylim([-1.5,1.5])


line1, = ax.plot(x.get_points(), y1.get_points())
line2, = ax.plot(x.get_points(), y2.get_points())
line3, = ax.plot(x.get_points(), y3.get_points())

# Continuously update the data and redraw the graph
while True:
    
    x.add_point(current_x)
    

    # Update the y data
    y1.add_point(np.sin(x.get_points()[-1])+0.2*np.random.rand())
    y2.add_point(np.sin(x.get_points()[-1])+ 0.5 + 0.2*np.random.rand())
    y3.add_point(np.sin(x.get_points()[-1])+ 1 + 0.2*np.random.rand())

    
    # Update the plot data
    line1.set_data(x.get_points(),y1.get_points())
    line2.set_data(x.get_points(),y2.get_points())
    line3.set_data(x.get_points(),y3.get_points())

    ax.set_xlim([current_x-Time2Display,current_x])

    # Redraw the plot
    fig.canvas.draw()
    current_x+=definition
    
    # Pause for the specified update frequency
    plt.pause(1/update_freq)
