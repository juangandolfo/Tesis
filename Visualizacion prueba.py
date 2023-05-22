import random
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
import threading
import time



class DataCollectionThread(threading.Thread):
    def __init__(self, graph_app):
        super().__init__()
        self.graph_app = graph_app
        self.running = threading.Event()

    def run(self):
        self.running.set()
        while self.running.is_set():
            self.graph_app.collect_data()
            time.sleep(1)

    def stop(self):
        self.running.clear()


class GraphApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Random Points Visualization")

        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111)
        self.points1 = []
        self.points2 = []
        self.points3 = []
        self.current_x = 0

        self.canvas = FigureCanvasTkAgg(self.fig, master=root)
        self.canvas.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.show_red = tk.BooleanVar()
        self.show_blue = tk.BooleanVar()
        self.show_green = tk.BooleanVar()
        self.show_red.set(True)
        self.show_blue.set(True)
        self.show_green.set(True)

        self.red_checkbox = tk.Checkbutton(root, text='Show Red', variable=self.show_red, command=self.update_line_visibility)
        self.red_checkbox.pack(anchor=tk.W)
        self.blue_checkbox = tk.Checkbutton(root, text='Show Blue', variable=self.show_blue, command=self.update_line_visibility)
        self.blue_checkbox.pack(anchor=tk.W)
        self.green_checkbox = tk.Checkbutton(root, text='Show Green', variable=self.show_green, command=self.update_line_visibility)
        self.green_checkbox.pack(anchor=tk.W)

        self.data_thread = DataCollectionThread(self)
        self.data_thread.start()

        self.update_graph()

    def collect_data(self):
        y1 = random.random()
        y2 = random.random()
        y3 = random.random()
        point1 = (self.current_x, y1)
        point2 = (self.current_x, y2)
        point3 = (self.current_x, y3)
        self.points1.append(point1)
        self.points2.append(point2)
        self.points3.append(point3)

        if len(self.points1) > 10:
            self.points1 = self.points1[1:]
            self.points2 = self.points2[1:]
            self.points3 = self.points3[1:]

        self.current_x += 1

    def update_graph(self):
        self.ax.clear()

        x_values1 = [point[0] for point in self.points1]
        y_values1 = [point[1] for point in self.points1]
        x_values2 = [point[0] for point in self.points2]
        y_values2 = [point[1] for point in self.points2]
        x_values3 = [point[0] for point in self.points3]
        y_values3 = [point[1] for point in self.points3]

        if self.show_red.get():
            self.ax.plot(x_values1, y_values1, 'ro-', label='Red Graph')
        if self.show_blue.get():
            self.ax.plot(x_values2, y_values2, 'bo-', label='Blue Graph')
        if self.show_green.get():
            self.ax.plot(x_values3, y_values3, 'green', label='Green Graph')

        self.ax.set_xlim(self.current_x - 10, self.current_x)
        self.ax.set_ylim(0, 1)
        self.ax.set_xlabel('X')
        self.ax.set_ylabel('Y')
        self.ax.set_title('Random Points Visualization')
        self.ax.legend()

        self.canvas.draw()
        self.root.after(1000, self.update_graph)

    def update_line_visibility(self):
        self.canvas.draw()

    def stop_data_collection(self):
        self.data_thread.stop()


if __name__ == "__main__":
    root = tk.Tk()
    app = GraphApp(root)
    root.mainloop()
    app.stop_data_collection()


