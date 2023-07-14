import random
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
import threading
import time
import matplotlib.gridspec as gridspec
import numpy as np
from scipy.signal import butter, filtfilt



class DataCollectionThread(threading.Thread):
    def __init__(self, graph_app):
        super().__init__()
        self.graph_app = graph_app
        self.running = threading.Event()

    def run(self):
        self.running.set()
        while self.running.is_set():
            self.graph_app.collect_data()
            time.sleep(1/80)

    def stop(self):
        self.running.clear()


class GraphApp:
    #parameters to modify graphs
    Sec2Display=5
    Sec2Save=50
    Sec2SaveLongHistory=5*60

    SampleFreq=2000
    
    NumDataPts2Display=SampleFreq*Sec2Display
    NumDataPts2Save = SampleFreq*Sec2Save
    
    def __init__(self, root):
        
        self.root = root
        self.root.title("Muscle and synergies activations visualization")
        self.fig = plt.figure()
        
        gs = gridspec.GridSpec(nrows=1, ncols=2, width_ratios=[1, 6])
        
        #agrego los subplots a la ventana
        self.ax = self.fig.add_subplot(gs[:,0])  # Add first graph to the left column
        self.ax2 = self.fig.add_subplot(gs[:,1])  # Add second graph to the right column
        
        # Code for the first Graph
        self.initVariables()

        # Code for the second Graph

        self.ax2.set_title("Second Graph")
        self.ax2.set_xlabel("Tiempo")
        self.ax2.set_ylabel("Actividad Muscular")

        # Code for the checkboxes

        self.canvas = FigureCanvasTkAgg(self.fig, master=root)
        self.canvas.get_tk_widget().pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        #Create the checkbutton and link it to variable
        Title1 = tk.Label(root, text="MUSCLES")
        Title1.pack()
        self.muscle1_checkbox = tk.Checkbutton(root, text='Show Muscle 1', variable=self.show_muscle1, command=self.update_line_visibility)
        self.muscle1_checkbox.pack(anchor=tk.W)
        self.muscle2_checkbox = tk.Checkbutton(root, text='Show Muscle 2', variable=self.show_muscle2, command=self.update_line_visibility)
        self.muscle2_checkbox.pack(anchor=tk.W)
        self.muscle3_checkbox = tk.Checkbutton(root, text='Show Muscle 3', variable=self.show_muscle3, command=self.update_line_visibility)
        self.muscle3_checkbox.pack(anchor=tk.W)
        self.muscle4_checkbox = tk.Checkbutton(root, text='Show Muscle 4', variable=self.show_muscle4, command=self.update_line_visibility)
        self.muscle4_checkbox.pack(anchor=tk.W)
        self.muscle5_checkbox = tk.Checkbutton(root, text='Show Muscle 5', variable=self.show_muscle5, command=self.update_line_visibility)
        self.muscle5_checkbox.pack(anchor=tk.W)
        self.muscle6_checkbox = tk.Checkbutton(root, text='Show Muscle 6', variable=self.show_muscle6, command=self.update_line_visibility)
        self.muscle6_checkbox.pack(anchor=tk.W)
        self.muscle7_checkbox = tk.Checkbutton(root, text='Show Muscle 7', variable=self.show_muscle7, command=self.update_line_visibility)
        self.muscle7_checkbox.pack(anchor=tk.W)
        self.muscle8_checkbox = tk.Checkbutton(root, text='Show Muscle 8', variable=self.show_muscle8, command=self.update_line_visibility)
        self.muscle8_checkbox.pack(anchor=tk.W)
        space1 = tk.Label(root, text="\n")
        space1.pack()
        
        Title2 = tk.Label(root, text="SYNERGIES")
        Title2.pack()
        self.synergy1_checkbox = tk.Checkbutton(root, text='Show Synergy 1', variable=self.show_synergy1, command=self.update_line_visibility)
        self.synergy1_checkbox.pack(anchor=tk.W)
        self.synergy2_checkbox = tk.Checkbutton(root, text='Show Synergy 2', variable=self.show_synergy2, command=self.update_line_visibility)
        self.synergy2_checkbox.pack(anchor=tk.W)
        self.synergy3_checkbox = tk.Checkbutton(root, text='Show Synergy 3', variable=self.show_synergy3, command=self.update_line_visibility)
        self.synergy3_checkbox.pack(anchor=tk.W)
        self.synergy4_checkbox = tk.Checkbutton(root, text='Show Synergy 4', variable=self.show_synergy4, command=self.update_line_visibility)
        self.synergy4_checkbox.pack(anchor=tk.W)
        self.synergy5_checkbox = tk.Checkbutton(root, text='Show Synergy 5', variable=self.show_synergy5, command=self.update_line_visibility)
        self.synergy5_checkbox.pack(anchor=tk.W)
        space2 = tk.Label(root, text="\n")
        space2.pack()

        Title3 = tk.Label(root, text="PRINT TO CONSOLE")
        Title3.pack()
        self.printHistory1_button = tk.Button(root, text='M1H', command=self.print_Muscle1History)
        self.printHistory1_button.pack()
        self.printHistory2_button = tk.Button(root, text='M2H', command=self.print_Muscle2History)
        self.printHistory2_button.pack()
        
        
        self.data_thread = DataCollectionThread(self)
        self.data_thread.start()

        self.update_graph()

    def collect_data(self):
        #collect the data from the server
                # now is randomized for testing
        y1 = random.gauss(0.8,0.1)
        y2 = random.gauss(0.5,0.1)
        y3 = random.gauss(0.1,0.1)
        point1 = (self.current_x, y1)
        point2 = (self.current_x, y2)
        point3 = (self.current_x, y3)
        
        #append to active display list and history list
        self.Muscle1.append(point1)
        self.Muscle2.append(point2)
        self.Muscle3.append(point3)
        self.Muscle1History.append(point1)
        self.Muscle2History.append(point2)
        self.Muscle3History.append(point3)

        #delete old data
        if len(self.Muscle1) > self.NumDataPts2Display:
            self.Muscle1 = self.Muscle1[1:]
        if len(self.Muscle2) > self.NumDataPts2Display:
            self.Muscle2 = self.Muscle2[1:]
        if len(self.Muscle3) > self.NumDataPts2Display:
            self.Muscle3 = self.Muscle3[1:]

        if len(self.Muscle1History) > self.NumDataPts2Save:
            self.Muscle1History = self.Muscle1History[1:]
        if len(self.Muscle2History) > self.NumDataPts2Save:
            self.Muscle2History = self.Muscle2History[1:]
        if len(self.Muscle3History) > self.NumDataPts2Save:
            self.Muscle3History = self.Muscle3History[1:]

        self.current_x += 1

    def update_graph(self):
        self.ax.clear()

        x_values1 = [point[0] for point in self.Muscle1] #cada punto trae [numMuestra,muestra]
        y_values1 = [point[1] for point in self.Muscle1]
        x_values2 = [point[0] for point in self.Muscle2]
        y_values2 = [point[1] for point in self.Muscle2]
        x_values3 = [point[0] for point in self.Muscle3]
        y_values3 = [point[1] for point in self.Muscle3]


        if self.show_muscle1.get():
            self.ax.plot(x_values1, y_values1, 'red', label='Red Graph')
        if self.show_muscle2.get():
            self.ax.plot(x_values2, y_values2, 'blue', label='Blue Graph')
        if self.show_muscle3.get():
            self.ax.plot(x_values3, y_values3, 'green', label='Green Graph')

        self.ax.set_xlim(self.current_x - 1000, self.current_x)
        self.ax.set_ylim(0, 1)
        self.ax.set_xlabel('Muscles')
        self.ax.set_ylabel('Activation')
        self.ax.set_title('Last 5 seconds of muscle activation')
        self.ax.legend() 

        # Create the bar graph for the second graph
        #tomando la ultima muestra
        
        last_sample1 = self.Muscle1[-1][1] if self.Muscle1 else 0
        last_sample2 = self.Muscle2[-1][1] if self.Muscle2 else 0
        last_sample3 = self.Muscle3[-1][1] if self.Muscle3 else 0

        #tomando con LPF
        '''last_sample1 = self.apply_low_pass_filter(x_values1, y_values1, 50) if self.muscle1 else 0
        last_sample2 = self.apply_low_pass_filter(x_values2, y_values2, 50) if self.muscle2 else 0
        last_sample3 = self.apply_low_pass_filter(x_values3, y_values3, 50) if self.muscle3 else 0'''

        # Create x-coordinates for the bars with an offset of 0.2
        x_bar = []
        heights = []
        muscles = []
        colorList = []
        if self.show_muscle1.get():
            #Create the positions for the x axis
            if x_bar != []:
                x_bar.append(x_bar[-1]+1)  
            else:  
                x_bar.append(0.2)
            #add the y value for it
            heights.append(last_sample1)
            # add label for the value added
            muscles.append('Muscle 1') 
            #add color, consistent with the previous graph
            colorList.append('Red')

        if self.show_muscle2.get(): 
            if x_bar != []:
                x_bar.append(x_bar[-1]+1)
            else:  
                x_bar.append(0.2) 
            heights.append(last_sample2)
            muscles.append('Muscle 2') 
            colorList.append('Blue')

        if self.show_muscle3.get():
            if x_bar != []:
                x_bar.append(x_bar[-1]+1)
            else:  
                x_bar.append(0.2) 
            heights.append(last_sample3)
            muscles.append('Muscle 3') 
            colorList.append('Green')

        self.ax2.clear()
        self.ax2.bar(x_bar, heights, color = colorList, edgecolor = 'black')
        self.ax2.set_ylim(0, 1)
        self.ax2.set_xticks(x_bar)
        self.ax2.set_xticklabels(muscles)
        self.ax2.set_xlabel('Muscles')
        self.ax2.set_ylabel('Activation')
        self.ax2.set_title('Muscle Activation')

        self.canvas.draw()
        self.root.after(10, self.update_graph)

    def update_line_visibility(self):
        self.canvas.draw()

    def stop_data_collection(self):
        self.data_thread.stop()

    def apply_low_pass_filter(self, x_values, y_values, window):
        if len(x_values) < window or len(y_values) < window:
            return 0.0  # Return default value if there are not enough samples

        # Apply low-pass filter using Butterworth filter from scipy
        sample_rate = 2000
        cutoff_frequency = 0.1  # Adjust as needed
        normalized_cutoff_frequency = cutoff_frequency / (0.5 * sample_rate)  # Normalize cutoff frequency
        b, a = butter(4, normalized_cutoff_frequency, btype='low', analog=False)
        filtered_y = filtfilt(b, a, y_values)

        # Retrieve the last filtered sample
        last_filtered_sample = filtered_y[-1]

        return last_filtered_sample

    def print_Muscle1History(self):
        formatted_list = '[{}]'.format('\n'.join('   '.join(map(str, item)) for item in self.Muscle1History))
        print(formatted_list)
    
    def print_Muscle2History(self):
        print(self.Muscle2History)
        
    def print_Muscle3History(self):
        print(self.Muscle1History)
        
    def print_Muscle4History(self):
        print(self.Muscle1History)
        
    def print_Muscle5History(self):
        print(self.Muscle1History)
        
    def print_Muscle6History(self):
        print(self.Muscle1History)
        
    def print_Muscle7History(self):
        print(self.Muscle1History)
        
    def print_Muscle8History(self):
        print(self.Muscle1History)
        
    def print_Synergy1History(self):
        print(self.Muscle1History)
        
    def print_Synergy2History(self):
        print(self.Muscle1History)
        
    def print_Synergy3History(self):
        print(self.Muscle1History)
        
    def print_Synergy4History(self):
        print(self.Muscle1History)
        
    def print_Synergy5History(self):
        print(self.Muscle1History)

    def initVariables(self):
        #create muscle and synergies lists
        self.current_x = 0

        self.Muscle1 = []
        self.Muscle2 = []
        self.Muscle3 = []
        self.Muscle4 = []
        self.Muscle5 = []
        self.Muscle6 = []
        self.Muscle7 = []
        self.Muscle8 = []
        self.Synergy1 = []
        self.Synergy2 = []
        self.Synergy3 = []
        self.Synergy4 = []
        self.Synergy5 = []

        self.Muscle1History = []
        self.Muscle2History = []
        self.Muscle3History = []
        self.Muscle4History = []
        self.Muscle5History = []
        self.Muscle6History = []
        self.Muscle7History = []
        self.Muscle8History = []
        self.Synergy1History = []
        self.Synergy2History = []
        self.Synergy3History = []
        self.Synergy4History = []
        self.Synergy5History = []

        #create and init variables for the checkboxes    
                
        self.show_muscle1 = tk.BooleanVar()
        self.show_muscle2 = tk.BooleanVar()
        self.show_muscle3 = tk.BooleanVar()
        self.show_muscle4 = tk.BooleanVar()
        self.show_muscle5 = tk.BooleanVar()
        self.show_muscle6 = tk.BooleanVar()
        self.show_muscle7 = tk.BooleanVar()
        self.show_muscle8 = tk.BooleanVar()
        self.show_synergy1 = tk.BooleanVar()
        self.show_synergy2 = tk.BooleanVar()
        self.show_synergy3 = tk.BooleanVar()
        self.show_synergy4 = tk.BooleanVar()
        self.show_synergy5 = tk.BooleanVar()
        
        #initialize the variables created
        self.show_muscle1.set(True)
        self.show_muscle2.set(True)
        self.show_muscle3.set(True)
        self.show_muscle4.set(True)
        self.show_muscle5.set(True)
        self.show_muscle6.set(True)
        self.show_muscle7.set(True)
        self.show_muscle8.set(True)
        self.show_synergy1.set(True) 
        self.show_synergy2.set(True)
        self.show_synergy3.set(True) 
        self.show_synergy4.set(True)
        self.show_synergy5.set(True)

if __name__ == "__main__":
    root = tk.Tk()
    app = GraphApp(root)
    root.mainloop()
    app.stop_data_collection()


