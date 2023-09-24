import random
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
import threading
#from threading import Semaphore
import time
import matplotlib.gridspec as gridspec
import numpy as np
from scipy.signal import butter, filtfilt

stack_lock = threading.Semaphore(1)

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
    startTime = time.time()
    startTime2 = time.time()
    MusclesNumber = 8
    SynergiesNumber = 5
    MusclesColors = ['red','blue','green','yellow','pink','brown','orange','violet']
    SynergiesColors = ['red','blue','green','yellow','pink']
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
        self.fig2= plt.figure()
        
        #divido el espacio y seteo el ratio
        gs = gridspec.GridSpec(nrows=3, ncols=2, width_ratios=[1, 1],height_ratios=[3,1,3])
        
        #agrego los subplots a la ventana
        self.DotsMuscles = self.fig.add_subplot(gs[0,0])  # Add first graph to the left column
        self.BarsMusculos = self.fig.add_subplot(gs[0,1])  # Add second graph to the right column
        
        self.DotsSynergies = self.fig.add_subplot(gs[2,0])
        self.barsSynergies = self.fig.add_subplot(gs[2,1])
        # Code for the first Graph
        self.initVariables()

        # labels for the second Graph
        self.BarsMusculos.set_title("Second Graph")
        self.BarsMusculos.set_xlabel("Tiempo")
        self.BarsMusculos.set_ylabel("Actividad Muscular")

        # Code for the checkboxes

        self.canvas = FigureCanvasTkAgg(self.fig, master=root)
        self.canvas.get_tk_widget().pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        #Create the checkbutton and link it to variable
        Title1 = tk.Label(root, text="MUSCLES")
        Title1.pack()
        self.musclesCheckboxes = [tk.Checkbutton(root, text='Show Muscle {}'.format(i+1), variable=self.ShowMuscles[i], command=self.update_line_visibility) for i in range(self.MusclesNumber)]
        for checkbox in self.musclesCheckboxes: 
            checkbox.pack(anchor=tk.W)
        space1 = tk.Label(root, text="\n")
        space1.pack()
        
        Title2 = tk.Label(root, text="SYNERGIES")
        Title2.pack()
        self.SynergiesCheckboxes =[tk.Checkbutton(root, text='Show Synergy {}'.format(i+1), variable=self.ShowSynergies[i], command=self.update_line_visibility) for i in range(self.SynergiesNumber)] 
        for checkbox in self.SynergiesCheckboxes: 
            checkbox.pack(anchor=tk.W)
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
        #print(time.time()-self.startTime)
        self.startTime= time.time()
        MuscleActivations = [random.gauss((i+1)/9,0.01) for i in range(self.MusclesNumber)]
        SynergiesActivations = [random.gauss((i+1)/6,0.01) for i in range(self.SynergiesNumber)]
        
        Musclespoints = [(self.current_x, MuscleActivations[i]) for i in range(self.MusclesNumber)]
        SynergiesPoints = [(self.current_x, SynergiesActivations[i]) for i in range(self.SynergiesNumber)]
        #append to active display list and history list
        stack_lock.acquire()
        for i in range(len(self.Muscles)):
            self.Muscles[i].append(Musclespoints[i])
            self.MusclesHistory[i].append(Musclespoints[i])

        for i in range(len(self.Synergies)):
            self.Synergies[i].append(SynergiesPoints[i])
            self.SynergiesHistory[i].append(SynergiesPoints[i])    
        
        #delete old data
        for i in range(len(self.Muscles)):
            if len(self.Muscles[i]) > self.NumDataPts2Display:
                self.Muscles[i] = self.Muscles[i][1:] 
        for i in range(len(self.MusclesHistory)):
            if (len(self.MusclesHistory)) > self.NumDataPts2Save:
                self.MusclesHistory[i] = self.MusclesHistory[i][1:]     
        
        for i in range(len(self.Synergies)):
            if len(self.Synergies[i]) > self.NumDataPts2Display:
                self.Synergies[i] = self.Synergies[i][1:]
        for i in range(len(self.SynergiesHistory)):
            if len(self.SynergiesHistory[i]) > self.NumDataPts2Save:
                self.SynergiesHistory[i] = self.SynergiesHistory[i][1:]
        
        self.current_x += 1
        stack_lock.release()

    def update_graph(self):
        print(time.time()-self.startTime2)
        self.startTime2= time.time()

        self.DotsMuscles.clear()
        self.DotsSynergies.clear()
        
        stack_lock.acquire()

        Muscles_x_values = [[point[0] for point in self.Muscles[i]] for i in range(len(self.Muscles))] #cada punto trae [numMuestra,muestra]
        Muscles_y_values = [[point[1] for point in self.Muscles[i]] for i in range(len(self.Muscles))]
        
        Synergies_x_values = [[point[0] for point in self.Synergies[i]] for i in range(len(self.Synergies))]
        Synergies_y_values = [[point[1] for point in self.Synergies[i]] for i in range(len(self.Synergies))]

        stack_lock.release()

        for i in range(len(self.ShowMuscles)):
            if self.ShowMuscles[i].get():
                '''try:
                    self.DotsMuscles.plot(Muscles_x_values[i], Muscles_y_values[i],self.MusclesColors[i], label='Muscle {}'.format(i+1))      
                except Exception as e:
                    print(e)
                    self.DotsMuscles.plot(Muscles_x_values[i], Muscles_y_values[i][:-1],self.MusclesColors[i], label='Muscle {}'.format(i+1))      
                '''
                self.DotsMuscles.plot(Muscles_x_values[i], Muscles_y_values[i],self.MusclesColors[i], label='Muscle {}'.format(i+1))
        for i in range(len(self.ShowSynergies)):
            if self.ShowSynergies[i].get():
                '''try:
                    self.DotsSynergies.plot(Synergies_x_values[i], Synergies_y_values[i],self.SynergiesColors[i], label='Synergy {}'.format(i+1))
                except Exception as e:
                    print(e)
                    self.DotsSynergies.plot(Synergies_x_values[i], Synergies_y_values[i][:-1],self.SynergiesColors[i], label='Synergy {}'.format(i+1))'''
                self.DotsSynergies.plot(Synergies_x_values[i], Synergies_y_values[i],self.SynergiesColors[i], label='Synergy {}'.format(i+1))
        self.DotsMuscles.set_xlim(self.current_x - 1000, self.current_x)
        self.DotsMuscles.set_ylim(0, 1)
        self.DotsMuscles.set_xlabel('Muscles')
        self.DotsMuscles.set_ylabel('Activation')
        self.DotsMuscles.set_title('Last 5 seconds of muscle activation')
        self.DotsMuscles.legend() 

        self.DotsSynergies.set_xlim(self.current_x - 1000, self.current_x)
        self.DotsSynergies.set_ylim(0, 1)
        self.DotsSynergies.set_xlabel('synergies')
        self.DotsSynergies.set_ylabel('Activation')
        self.DotsSynergies.set_title('Last 5 seconds of synergies activation')
        self.DotsSynergies.legend() 

        # Create the bar graph for the second graph
        #tomando la ultima muestra
        last_samples_muscles = [(self.Muscles[i][-1][1] if self.Muscles[1] else 0) for i in range(len(self.Muscles))]
        last_samples_synergies= [(self.Synergies[i][-1][1] if self.Synergies[1] else 0) for i in range(len(self.Synergies))]

        #tomando con LPF
        '''last_sample1 = self.apply_low_pass_filter(x_values1, y_values1, 50) if self.muscle1 else 0
        last_sample2 = self.apply_low_pass_filter(x_values2, y_values2, 50) if self.muscle2 else 0
        last_sample3 = self.apply_low_pass_filter(x_values3, y_values3, 50) if self.muscle3 else 0'''

        # Create x-coordinates for the bars with an offset of 0.2
        x_bar_muscles = []
        heights_muscles = []
        musclesList = []
        colorListMuscle = []
        for i in range(len(self.ShowMuscles)):
            if self.ShowMuscles[i].get():
                if x_bar_muscles != []:
                    x_bar_muscles.append(x_bar_muscles[-1]+1)  
                else:  
                    x_bar_muscles.append(0.2)
                #add the y value for it
                heights_muscles.append(last_samples_muscles[i])
                # add label for the value added
                musclesList.append('Muscle {}'.format(i+1)) 
                #add color, consistent with the previous graph
                colorListMuscle.append(self.MusclesColors[i])
    
        self.BarsMusculos.clear()
        self.BarsMusculos.bar(x_bar_muscles, heights_muscles, color = colorListMuscle, edgecolor = 'black')
        self.BarsMusculos.set_ylim(0, 1)
        self.BarsMusculos.set_xticks(x_bar_muscles)
        self.BarsMusculos.set_xticklabels(musclesList)
        self.BarsMusculos.set_xlabel('Muscles')
        self.BarsMusculos.set_ylabel('Activation')
        self.BarsMusculos.set_title('Muscle Activation')
        for tick in self.BarsMusculos.get_xticklabels():
            tick.set_rotation(30)

        # Create x-coordinates for the bars with an offset of 0.2
        x_bar_synergies = []
        heights_synergies = []
        synergiesList = []
        colorListsynergies = []
        for i in range(len(self.ShowSynergies)):
            if self.ShowSynergies[i].get():
                if x_bar_synergies != []:
                    x_bar_synergies.append(x_bar_synergies[-1]+1)  
                else:  
                    x_bar_synergies.append(0.2)
                #add the y value for it
                heights_synergies.append(last_samples_synergies[i])
                # add label for the value added
                synergiesList.append('synergies {}'.format(i+1)) 
                #add color, consistent with the previous graph
                colorListsynergies.append(self.SynergiesColors[i])
    
        self.barsSynergies.clear()
        self.barsSynergies.bar(x_bar_synergies, heights_synergies, color = colorListsynergies, edgecolor = 'black')
        self.barsSynergies.set_ylim(0, 1)
        self.barsSynergies.set_xticks(x_bar_synergies)
        self.barsSynergies.set_xticklabels(synergiesList)
        self.barsSynergies.set_xlabel('synergies')
        self.barsSynergies.set_ylabel('Activation')
        self.barsSynergies.set_title('synergy Activation')
        for tick in self.barsSynergies.get_xticklabels():
            tick.set_rotation(30)    

 
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
        formatted_list = '[{}]'.format('\n'.join('   '.join(map(str, item)) for item in self.MusclesHistory[1]))
        print(formatted_list)
    
    def print_Muscle2History(self):
        print(self.MusclesHistory[2])
        
    def print_Muscle3History(self):
        self.fig2.draw()
        
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

        self.Muscles = [[] for _ in range(self.MusclesNumber)]    
        self.MusclesHistory = [[] for _ in range(self.MusclesNumber)]
        self.Synergies = [[] for _ in range(self.SynergiesNumber)]
        self.SynergiesHistory = [[] for _ in range(self.SynergiesNumber)]

        #create and init variables for the checkboxes           
        self.ShowMuscles = [tk.BooleanVar() for _ in range(self.MusclesNumber)]
        self.ShowSynergies = [tk.BooleanVar() for _ in range(self.SynergiesNumber)]
        
        #initialize the variables created
        for show_muscle in self.ShowMuscles:
            show_muscle.set(True)
        for show_synergy in self.ShowSynergies:
            show_synergy.set(True)
        

if __name__ == "__main__":
    root = tk.Tk()
    app = GraphApp(root)
    root.mainloop()
    app.stop_data_collection()


