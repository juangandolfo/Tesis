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
    def __init__(self, root):
        
        self.root = root
        self.root.title("Random Points Visualization")
        self.fig = plt.figure()
        gs = gridspec.GridSpec(1, 2, width_ratios=[1, 1.5])  # Create a 1x2 grid with different width ratios

        self.ax = self.fig.add_subplot(gs[0])  # Add first graph to the left column
        self.ax2 = self.fig.add_subplot(gs[1])  # Add second graph to the right column

        # Code for the first Graph
        #self.ax = self.fig.add_subplot(111)

        self.muscle1 = []
        self.muscle2 = []
        self.muscle3 = []
        self.current_x = 0

        self.history1 = []
        self.history2 = []
        self.history3 = []

        # Code for the second Graph

        self.ax2.set_title("Second Graph")
        self.ax2.set_xlabel("Tiempo")
        self.ax2.set_ylabel("Actividad Muscular")

        # Code for the checkboxes

        self.canvas = FigureCanvasTkAgg(self.fig, master=root)
        self.canvas.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.show_red = tk.BooleanVar()
        self.show_blue = tk.BooleanVar()
        self.show_green = tk.BooleanVar()

        self.show_PrintHistory1 = tk.BooleanVar()
        
        self.show_red.set(True)
        self.show_blue.set(True)
        self.show_green.set(True)
        
        self.show_PrintHistory1.set(False)

        self.red_checkbox = tk.Checkbutton(root, text='Show Red', variable=self.show_red, command=self.update_line_visibility)
        self.red_checkbox.pack(anchor=tk.W)
        self.blue_checkbox = tk.Checkbutton(root, text='Show Blue', variable=self.show_blue, command=self.update_line_visibility)
        self.blue_checkbox.pack(anchor=tk.W)
        self.green_checkbox = tk.Checkbutton(root, text='Show Green', variable=self.show_green, command=self.update_line_visibility)
        self.green_checkbox.pack(anchor=tk.W)

        self.printHistory1_checkbox = tk.Checkbutton(root, text='printHistory1', variable=self.show_PrintHistory1, command=self.update_line_visibility)
        self.printHistory1_checkbox.pack(anchor=tk.W)

        self.data_thread = DataCollectionThread(self)
        self.data_thread.start()

        self.update_graph()

    def collect_data(self):
        y1 = random.gauss(0.8,0.1)
        y2 = random.gauss(0.5,0.1)
        y3 = random.gauss(0.1,0.1)
        point1 = (self.current_x, y1)
        point2 = (self.current_x, y2)
        point3 = (self.current_x, y3)
        
        self.muscle1.append(point1)
        self.muscle2.append(point2)
        self.muscle3.append(point3)
        self.history1.append(point1)
        self.history2.append(point2)
        self.history3.append(point3)

        if len(self.muscle1) > 1000:
            self.muscle1 = self.muscle1[1:]
        if len(self.muscle2) > 1000:
            self.muscle2 = self.muscle2[1:]
        if len(self.muscle3) > 1000:
            self.muscle3 = self.muscle3[1:]

        if len(self.history1) > 10000:
            self.history1 = self.history1[1:]
        if len(self.history2) > 10000:
            self.history2 = self.history2[1:]
        if len(self.history3) > 10000:
            self.history3 = self.history3[1:]

        self.current_x += 1

    def update_graph(self):
        self.ax.clear()

        x_values1 = [point[0] for point in self.muscle1]
        y_values1 = [point[1] for point in self.muscle1]
        x_values2 = [point[0] for point in self.muscle2]
        y_values2 = [point[1] for point in self.muscle2]
        x_values3 = [point[0] for point in self.muscle3]
        y_values3 = [point[1] for point in self.muscle3]


        if self.show_red.get():
            self.ax.plot(x_values1, y_values1, 'red', label='Red Graph')
        if self.show_blue.get():
            self.ax.plot(x_values2, y_values2, 'blue', label='Blue Graph')
        if self.show_green.get():
            self.ax.plot(x_values3, y_values3, 'green', label='Green Graph')
        if self.show_PrintHistory1.get():
            print(self.muscle1)
            print(self.history1)
            '''
            last_filtered_sample1 = self.apply_low_pass_filter(x_values1, y_values1, 100)
            last_filtered_sample2 = self.apply_low_pass_filter(x_values2, y_values2, 100)
            last_filtered_sample3 = self.apply_low_pass_filter(x_values3, y_values3, 100)

            print(last_filtered_sample1)
            print(last_filtered_sample2)
            print(last_filtered_sample3)'''
            self.show_PrintHistory1.set(False)

        self.ax.set_xlim(self.current_x - 1000, self.current_x)
        self.ax.set_ylim(0, 1)
        self.ax.set_xlabel('X')
        self.ax.set_ylabel('Y')
        self.ax.set_title('Random Points Visualization')
        self.ax.legend() 

        # Create the bar graph for the second graph
        #tomando la ultima muestra
        
        last_sample1 = self.muscle1[-1][1] if self.muscle1 else 0
        last_sample2 = self.muscle2[-1][1] if self.muscle2 else 0
        last_sample3 = self.muscle3[-1][1] if self.muscle3 else 0

        #tomando con LPF
        '''last_sample1 = self.apply_low_pass_filter(x_values1, y_values1, 50) if self.muscle1 else 0
        last_sample2 = self.apply_low_pass_filter(x_values2, y_values2, 50) if self.muscle2 else 0
        last_sample3 = self.apply_low_pass_filter(x_values3, y_values3, 50) if self.muscle3 else 0'''

        # Create x-coordinates for the bars with an offset of 0.2
        x_bar = np.array([0, 1, 2]) + 0.2
        # Heights of the bars: last samples for each muscle and the maximum value of 1.0 for the gray portion
        heights = [last_sample1, last_sample2, last_sample3]

        self.ax2.clear()
        # Create the bar graph


        self.ax2.bar(x_bar, heights, color=['red', 'blue', 'green', 'lightgrey'], edgecolor='black')
        self.ax2.set_ylim(0, 1)
        self.ax2.set_xticks([0.2, 1.2, 2.2])
        self.ax2.set_xticklabels(['Muscle 1', 'Muscle 2', 'Muscle 3'])
        self.ax2.set_xlabel('Muscles')
        self.ax2.set_ylabel('Activation')


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

if __name__ == "__main__":
    root = tk.Tk()
    app = GraphApp(root)
    root.mainloop()
    app.stop_data_collection()


