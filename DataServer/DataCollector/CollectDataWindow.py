"""
Data Collector GUI
This is the GUI that lets you connect to a base, scan via rf for sensors, and stream data from them in real time.
"""

import sys
from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
from DataServer.DataCollector.CollectDataController import *
import tkinter as tk
from tkinter import filedialog
#from Plotter import GenericPlot as gp
import DataServer.API_Parameters as params
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import pymsgbox as msgbox
import os 
import json
import ExportData



class CollectDataWindow(QWidget):
    def __init__(self,controller):
        QWidget.__init__(self)
        self.pipelinetext = "Off"
        self.controller = controller
        self.buttonPanel = self.ButtonPanel()
        self.calibration_window = CalibrationWindow()
        layout = QHBoxLayout()
        self.setStyleSheet("background-color:#DDDDDD;")
        layout.addWidget(self.buttonPanel)
        self.setLayout(layout)
        self.setWindowTitle("Collect Data GUI")

        #---- Connect the controller to the GUI
        self.CallbackConnector = PlottingManagement()
    
    #-----------------------------------------------------------------------
    #---- GUI Components
    def ButtonPanel(self):
        buttonPanel = QWidget()
        buttonLayout = QVBoxLayout()

        self.pipelinelabel = QLabel('Pipeline State', self)
        self.pipelinelabel.setAlignment(Qt.AlignCenter)
        self.pipelinelabel.setStyleSheet("color:#000066")
        buttonLayout.addWidget(self.pipelinelabel)

        self.pipelinestatelabel = QLabel(self.pipelinetext, self)
        self.pipelinestatelabel.setAlignment(Qt.AlignCenter)
        self.pipelinestatelabel.setStyleSheet("color:#000066")
        buttonLayout.addWidget(self.pipelinestatelabel)

        #---- Connect Button
        self.read_button = QPushButton('Connect', self)
        self.read_button.setToolTip('Connect Base')
        self.read_button.setSizePolicy(QSizePolicy.Preferred,QSizePolicy.Expanding)
        self.read_button.objectName = 'Connect'
        self.read_button.clicked.connect(self.connect_callback)
        self.read_button.setStyleSheet('QPushButton {background-color: #4CAF50; color: #FFFFFF;}')
        self.read_button.setEnabled(True)
        buttonLayout.addWidget(self.read_button)

        findSensor_layout = QHBoxLayout()
        
        #---- Pair Button
        self.pair_button = QPushButton('Pair', self)
        self.pair_button.setToolTip('Pair Sensors')
        self.pair_button.setSizePolicy(QSizePolicy.Preferred,QSizePolicy.Expanding)
        self.pair_button.objectName = 'Pair'
        self.pair_button.clicked.connect(self.pair_callback)
        self.pair_button.setStyleSheet('QPushButton {color: #000066;}')
        self.pair_button.setEnabled(False)
        findSensor_layout.addWidget(self.pair_button)

        #---- Scan Button
        self.scan_button = QPushButton('Scan', self)
        self.scan_button.setToolTip('Scan for Sensors')
        self.scan_button.setSizePolicy(QSizePolicy.Preferred,QSizePolicy.Expanding)
        self.scan_button.objectName = 'Scan'
        self.scan_button.clicked.connect(self.scan_callback)
        self.scan_button.setStyleSheet('QPushButton {color: #000066;}')
        self.scan_button.setEnabled(False)
        findSensor_layout.addWidget(self.scan_button)

        buttonLayout.addLayout(findSensor_layout)

        ''' #---- Start Button
        self.start_button = QPushButton('Start', self)
        self.start_button.setToolTip('Start Sensor Stream')
        self.start_button.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.start_button.objectName = 'Start'
        self.start_button.clicked.connect(self.start_callback)
        self.start_button.setStyleSheet('QPushButton {color: #000066;}')
        self.start_button.setEnabled(False)
        buttonLayout.addWidget(self.start_button)'''

        '''#---- Stop Button
        self.stop_button = QPushButton('Stop', self)
        self.stop_button.setToolTip('Stop Sensor Stream')
        self.stop_button.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.stop_button.objectName = 'Stop'
        self.stop_button.clicked.connect(self.stop_callback)
        self.stop_button.setStyleSheet('QPushButton {color: #000066;}')
        self.stop_button.setEnabled(False)
        buttonLayout.addWidget(self.stop_button)'''

        '''#---- Reset Button
        self.reset_button = QPushButton('Reset Pipeline', self)
        self.reset_button.setToolTip('Disarm Pipeline')
        self.reset_button.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.reset_button.objectName = 'Reset'
        self.reset_button.clicked.connect(self.reset_callback)
        self.reset_button.setStyleSheet('QPushButton {color: #000066;}')
        self.reset_button.setEnabled(False)
        buttonLayout.addWidget(self.reset_button)'''

        #---- Configure Sensors Button
        self.configure_button = QPushButton('Configure Sensors', self)
        self.configure_button.setToolTip('Configure Sensors')
        self.configure_button.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.configure_button.objectName = 'Configure Sensors'
        self.configure_button.clicked.connect(self.ConfigureSensors_callback)  # Connect to the callback method
        self.configure_button.setStyleSheet('QPushButton {color: #000066;}')
        self.configure_button.setEnabled(False)
        buttonLayout.addWidget(self.configure_button)

        '''#---- Drop-down menu of sensor modes
        self.SensorModeList = QComboBox(self)
        self.SensorModeList.setToolTip('Sensor Modes')
        self.SensorModeList.objectName = 'PlaceHolder'
        self.SensorModeList.setStyleSheet('QComboBox {color: #000066;background: #848482}')
        self.SensorModeList.currentIndexChanged.connect(self.sensorModeList_callback)
        #buttonLayout.addWidget(self.SensorModeList)'''

        #---- List of detected sensors
        self.SensorListBox = QListWidget(self)
        self.SensorListBox.setToolTip('Sensor List')
        self.SensorListBox.objectName = 'PlaceHolder'
        self.SensorListBox.setStyleSheet('QListWidget {color: #000066;background:#848482}')
        #self.SensorListBox.clicked.connect(self.sensorList_callback)
        buttonLayout.addWidget(self.SensorListBox)

         #---- Calibration Button
        self.calibration_button = QPushButton('Start Calibration', self)
        self.calibration_button.setToolTip('Start Calibration')
        self.calibration_button.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.calibration_button.objectName = 'Start Calibration'
        self.calibration_button.clicked.connect(self.calibration_callback)  # Connect to the callback method
        self.calibration_button.setStyleSheet('QPushButton {color: #000066;}')
        self.calibration_button.setEnabled(False)
        buttonLayout.addWidget(self.calibration_button)

        #---- Start Cursor Button
        self.cursor_button = QPushButton('Cursor Game', self)
        self.cursor_button.setToolTip('Start Cursor')
        self.cursor_button.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.cursor_button.objectName = 'Start Cursor'
        self.cursor_button.clicked.connect(self.start_cursor)
        self.cursor_button.setStyleSheet('QPushButton {color: #000066;}')
        self.cursor_button.setEnabled(False)
        buttonLayout.addWidget(self.cursor_button)

        #---- Start Visualization Button
        self.visualization_button = QPushButton('Visualization', self)
        self.visualization_button.setToolTip('Start Visualization')
        self.visualization_button.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.visualization_button.objectName = 'Start Visualization'
        self.visualization_button.clicked.connect(self.start_visualization)
        self.visualization_button.setStyleSheet('QPushButton {color: #000066;}')
        self.visualization_button.setEnabled(False)
        buttonLayout.addWidget(self.visualization_button)

        #---- Export Data Button
        self.export_button = QPushButton('Export Data', self)
        self.export_button.setToolTip('Export Data')
        self.export_button.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.export_button.objectName = 'Export Data'
        self.export_button.clicked.connect(self.export_data)
        self.export_button.setStyleSheet('QPushButton {color: #000066;}')
        self.export_button.setEnabled(False)
        buttonLayout.addWidget(self.export_button)

        #---- Home Button
        button = QPushButton('Home', self)
        button.setToolTip('Return to Start Menu')
        button.objectName = 'Home'
        button.clicked.connect(self.home_callback)
        button.setStyleSheet('QPushButton {color: #000066;}')
        buttonLayout.addWidget(button)

        buttonPanel.setLayout(buttonLayout)

        return buttonPanel

    #-----------------------------------------------------------------------
    #---- Callback Functions
    def getpipelinestate(self):
        self.pipelinetext = self.CallbackConnector.PipelineState_Callback()
        self.pipelinestatelabel.setText(self.pipelinetext)

    def connect_callback(self):
        self.CallbackConnector.Connect_Callback()
        self.read_button.setEnabled(False)
        self.read_button.setStyleSheet('QPushButton {color: #000066;}')
        self.scan_button.setStyleSheet('QPushButton {background-color: #4CAF50; color: #FFFFFF;}')
        self.scan_button.setEnabled(True)

        self.scan_button.setEnabled(True)
        self.getpipelinestate()
        self.pipelinestatelabel.setText(self.pipelinetext + " (Base Connected)")

    def pair_callback(self):
        self.CallbackConnector.Pair_Callback()
        self.scan_callback()
        self.getpipelinestate()

    def scan_callback(self):
        sensorList = self.CallbackConnector.Scan_Callback()
        self.SensorListBox.clear()
        self.SensorListBox.addItems(sensorList)
        self.SensorListBox.setCurrentRow(0)

        if len(sensorList)>0:
            self.calibration_button.setEnabled(True)
        self.getpipelinestate()

        self.configure_button.setEnabled(True)
        self.configure_button.setStyleSheet('QPushButton {background-color: #4CAF50; color: #FFFFFF;}')
        self.calibration_button.setEnabled(False)
        self.calibration_button.setStyleSheet('QPushButton {color: #000066;}')

    '''def start_callback(self):
        self.CallbackConnector.Start_Callback()'''

    '''def stop_callback(self):
        self.CallbackConnector.Stop_Callback()
        self.reset_button.setEnabled(True)
        self.getpipelinestate()'''

    '''def reset_callback(self):
        self.CallbackConnector.Reset_Callback()
        self.getpipelinestate()
        self.reset_button.setEnabled(False)'''

    def home_callback(self):
        self.controller.showStartMenu()

    def sensorList_callback(self):
        curItem = self.SensorListBox.currentRow()
        modeList = self.CallbackConnector.getSampleModes(curItem)
        curModes = self.CallbackConnector.getCurMode()

        self.SensorModeList.clear()
        self.SensorModeList.addItems(modeList)
        self.SensorModeList.setCurrentText(curModes[0])

    def sensorModeList_callback(self):
        curItem = self.SensorListBox.currentRow()
        selMode = self.SensorModeList.currentText()
        if selMode != '':
            self.CallbackConnector.setSampleMode_hardcoded()
    
    def ConfigureSensors_callback(self):
        self.CallbackConnector.setSampleMode_hardcoded()
        self.CallbackConnector.FinishInitialization()

        self.configure_button.setEnabled(False)
        self.configure_button.setStyleSheet('QPushButton {color: #000066;}')
        self.calibration_button.setEnabled(True)
        self.calibration_button.setStyleSheet('QPushButton {background-color: #4CAF50; color: #FFFFFF;}')

    def calibration_callback(self):
        params.StartCalibration = True
        self.calibration_window.show()
        self.CallbackConnector.StartCalibration_Callback()
        self.scan_button.setEnabled(False)
        self.scan_button.setStyleSheet('QPushButton {color: #000066;}')
        self.configure_button.setEnabled(False)
        self.configure_button.setStyleSheet('QPushButton {color: #000066;}')
        self.visualization_button.setEnabled(True)
        self.visualization_button.setStyleSheet('QPushButton {background-color: #4CAF50; color: #FFFFFF;}')
        self.cursor_button.setEnabled(True)
        self.cursor_button.setStyleSheet('QPushButton {background-color: #4CAF50; color: #FFFFFF;}')

    def start_cursor(self):
        self.CallbackConnector.StartCursor_Callback()

    def start_visualization(self):
        self.CallbackConnector.StartVisualization_Callback()
    
    def export_data(self):
        # Replace these paths with your actual local folder and OneDrive sync folder
        local_folder = r"C:\Users\melis\OneDrive\Documents\GitHub\Tesis\ExperimentsFiles"
        onedrive_folder = r"C:\Users\melis\OneDrive - Universidad Católica del Uruguay\Tesis\Etapa Caracterización\Experimental Data"
        ExportData.upload_folder_to_onedrive(local_folder, onedrive_folder)


class SimulationWindow(QWidget):
    def __init__(self, controller, config_folder):
        super(SimulationWindow, self).__init__()  # Properly call the base class initializer
        self.config_folder = config_folder
        self.controller = controller
        self.config_file = "Calibration.json"
        self.events_file = "Events.json"
        self.raw_data_file = "RawData.csv"
        self.colors = ['Red', 'Blue', 'Yellow', 'Green', 'Orange', 'Purple', 'Grey', 'Brown']

        # Create the main layout
        main_layout = QHBoxLayout()
        self.setStyleSheet("background-color:#DDDDDD;")

        # Add button panel
        self.buttonPanel = self.ButtonPanel()
        main_layout.addWidget(self.buttonPanel)

        # Add plotting area
        self.plotting_area = self.create_plotting_area()
        main_layout.addWidget(self.plotting_area)

        self.setLayout(main_layout)
        self.setWindowTitle("Simulation GUI")

        # Populate the config dropdown with experiment folders
        self.populate_config_dropdown()

        # Connect the controller to the GUI
        self.CallbackConnector = PlottingManagement()  # Replace with your actual connector if needed

    def ButtonPanel(self):
        buttonPanel = QWidget()
        buttonLayout = QVBoxLayout()

        # Configuration File Dropdown (Only Experiment Folder Selection)
        self.config_label = QLabel("Select the experiment folder:", self)
        self.config_label.setFixedSize(200, 50)
        self.config_label.setAlignment(Qt.AlignCenter)
        self.config_label.setStyleSheet("color:#000066;")
        buttonLayout.addWidget(self.config_label)

        self.config_dropdown = QComboBox(self)
        self.config_dropdown.setToolTip("Select an experiment folder")
        self.config_dropdown.setStyleSheet("QComboBox {color: #000066; background: #848482;}")
        self.config_dropdown.currentIndexChanged.connect(self.config_file_selected)
        buttonLayout.addWidget(self.config_dropdown)

        # Placeholder dropdown for attempts (hidden initially)
        self.attempts_label = QLabel("Select an attempt:", self)
        self.attempts_label.setFixedSize(200, 50)
        self.attempts_label.setAlignment(Qt.AlignCenter)
        self.attempts_label.setStyleSheet("color:#000066;")
        self.attempts_label.hide()  # Initially hidden
        buttonLayout.addWidget(self.attempts_label)

        self.attempts_dropdown = QComboBox(self)
        self.attempts_dropdown.setToolTip("Select an attempt")
        self.attempts_dropdown.setStyleSheet("QComboBox {color: #000066; background: #848482;}")
        self.attempts_dropdown.currentIndexChanged.connect(self.attempt_selected)
        self.attempts_dropdown.hide()  # Initially hidden
        buttonLayout.addWidget(self.attempts_dropdown)

        self.attempt_info_label = QLabel("Attempt details")
        self.attempt_info_label.hide()
        buttonLayout.addWidget(self.attempt_info_label)

        # Connect Button
        self.read_button = QPushButton('Read Experiment Files', self)
        self.read_button.setFixedSize(200, 50)
        self.read_button.setToolTip('Read Experiment Files')
        self.read_button.clicked.connect(self.upload_experiment)
        self.read_button.setStyleSheet('QPushButton {color: #000066;}')
        buttonLayout.addWidget(self.read_button)

       # Start Simulation Button
        start_simulation_button = QPushButton('Start Simulation', self)
        start_simulation_button.setFixedSize(200, 50)
        start_simulation_button.setToolTip('Start Simulation')
        start_simulation_button.clicked.connect(self.start_simulation_callback)
        start_simulation_button.setStyleSheet('QPushButton {color: #000066;}')
        buttonLayout.addWidget(start_simulation_button)

        # Start Simulation Cursor
        start_cursor_simulation = QPushButton('Start Cursor', self)
        start_cursor_simulation.setFixedSize(200, 50)
        start_cursor_simulation.setToolTip('Start Cursor')
        start_cursor_simulation.clicked.connect(self.start_cursor_simulation)
        start_cursor_simulation.setStyleSheet('QPushButton {color: #000066;}')
        buttonLayout.addWidget(start_cursor_simulation)

        # Home Button
        home_button = QPushButton('Home', self)
        home_button.setFixedSize(200, 50)
        home_button.setToolTip('Return to Start Menu')
        home_button.clicked.connect(self.home_callback)
        home_button.setStyleSheet('QPushButton {color: #000066;}')
        buttonLayout.addWidget(home_button)

        buttonPanel.setLayout(buttonLayout)
        return buttonPanel

    def create_plotting_area(self):
        """Create a plotting area using Matplotlib."""
        plot_widget = QWidget()
        layout = QVBoxLayout()

        # Create a Matplotlib figure
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)

        layout.addWidget(self.canvas)
        plot_widget.setLayout(layout)
        plot_widget.setFixedSize(1000, 800)
        return plot_widget

    def upload_experiment(self):
        # Get the selected experiment folder from the dropdown
        selected_folder = self.config_dropdown.currentText()
        self.selected_folder_path = os.path.join(self.config_folder, selected_folder)

        # Check if the specified .json configuration file exists in the selected folder
        config_file_path = os.path.join(self.selected_folder_path, self.config_file)
        if not os.path.exists(config_file_path):
            print(f"No file named {self.config_file} found in {self.selected_folder_path}")
            return
        # Read the .json file
        with open(config_file_path, 'r') as json_file:
            json_data = json.load(json_file)

        # Extract the data from the JSON into variables
        self.angles = json_data['Angles']
        self.muscles_number = json_data['MusclesNumber']
        self.peaks = json_data['Peaks']
        self.sensor_stickers = json_data['SensorStickers']
        self.synergy_base = json_data['SynergyBase']
        self.thresholds = json_data['Thresholds']
        
        # print("Angles:", self.angles)
        # print("MusclesNumber:", self.muscles_number)
        # print("Peaks:", self.peaks)
        # print("SensorStickers:", self.sensor_stickers)
        # print("SynergyBase:", self.synergy_base)
        # print("Thresholds:", self.thresholds)

        # Check if the specified .json file exists in the selected folder
        events_file_path = os.path.join(self.selected_folder_path, self.events_file)
        if not os.path.exists(events_file_path):
            print(f"No file named {self.events_file} found in {self.selected_folder_path}")
            return
        # Read the .json file
        with open(events_file_path, 'r') as json_file:
            json_data = json.load(json_file)
        
        # # Create a list to store all attempts
        # self.attempts_data = []

        # # Extract the data from the JSON into variables
        # for attempt in json_data:  # Use json_data, not json_file
        #     attempt_info = {
        #         "attemptNumber": attempt["attemptNumber"],
        #         "start_Timestamp": attempt["start_Timestamp"],
        #         "end_Timestamp": attempt["end_Timestamp"],
        #         "result": attempt["result"],
        #     }
        #     self.attempts_data.append(attempt_info)  # Append each attempt to the list

        # Print or process all attempts
        # for attempt_info in attempts_data:
        #     print(f"Attempt {attempt_info['attemptNumber']}:")
        #     print(f"  Start: {attempt_info['start_Timestamp']}")
        #     print(f"  End: {attempt_info['end_Timestamp']}")
        #     print(f"  Result: {attempt_info['result']}")

        # Populate the dropdown with attempts
        self.attempts_dropdown.clear()  # Clear any existing items
        for attempt in json_data:
            self.attempts_dropdown.addItem(f"Attempt {attempt['Id']}", attempt)

        # Show the dropdown and label
        self.attempts_label.show()
        self.attempts_dropdown.show()
        
        # Logic to handle experiment file upload and data processing
        self.plot_data()

    def plot_data(self):
        self.figure.clear()
        self.synergiesNumber = np.array(self.synergy_base).shape[0]
        gs = self.figure.add_gridspec(self.synergiesNumber, 2)  
        
        # Plot Synergy Base ----------------------------------------------
        for i in range (1, self.synergiesNumber+1):
            ax = self.figure.add_subplot(gs[i-1, 0])
            ax.bar(range(np.asarray(self.synergy_base).shape[1]), self.synergy_base[i-1], color=self.colors[i-1], alpha=0.6)
            ax.set_ylim(0, 1)  # Set y-axis limits to be between 0 and 0.5
            ax.set_xlim(-0.5, self.muscles_number-0.5) 
            ax.set_xticks(range(self.muscles_number))  # Ensure all ticks are visible
            ax.set_yticks([0, 0.5, 1])  # Ensure y-ticks are visible

            if i == 1:
                ax.set_title(f'Synergy Basis ({self.synergiesNumber} Synergies)')
                ax.set_xlabel('Muscles')  # X-axis label
                ax.set_ylabel('Relative Activation')  # Y-axis label
                ax.set_xticklabels(self.sensor_stickers)
                ax.set_yticklabels([str(tick) for tick in [0, 0.5, 1]])
            else: 
                ax.set_xticklabels([''] * self.muscles_number)  # Remove x-axis tick labels but keep the ticks
                ax.set_yticklabels([''] * 3)  # Remove y-axis tick labels but keep the ticks
            
        # Plot Projection Angles ----------------------------------------------
        ax = self.figure.add_subplot(gs[:, 1], polar=True)
        ax.set_title("Projection Angles")
        for i in range(len(self.angles)):
            theta = np.radians(int(self.angles[i]))  # Convert to radians
            ax.plot([0, theta], [0, 1], marker='o', color=self.colors[i])  # Plot the vector
        
        # Adjust the layout to expand subplots
        self.figure.tight_layout()
        self.figure.subplots_adjust(hspace=0.8, wspace=0.6)  # Adjust the spacing if needed
        self.canvas.draw()

    def home_callback(self):
        self.controller.showStartMenu()

    def start_simulation_callback(self):
        params.csvFile = os.path.join(self.selected_folder_path, self.raw_data_file)

        self.CallbackConnector.Connect_Callback()
        time.sleep(0.1)
        self.CallbackConnector.Scan_Callback()
        time.sleep(0.1)
        self.CallbackConnector.setSampleMode_hardcoded()
        time.sleep(0.1)
        self.CallbackConnector.StartCalibration_Callback()
        
        #UploadCalibration 
        params.Thresholds = self.thresholds
        params.Peaks = self.peaks
        params.AnglesOutput = self.angles
        params.SynergyBase = self.synergy_base
        params.SensorStickers = self.sensor_stickers
        params.SynergiesNumber = len(self.angles)
        params.SimulationCalibration = True
        time.sleep(1)
        self.CallbackConnector.StartCursor_Callback()
        
    
    def start_cursor_simulation(self):
        self.CallbackConnector.StartCursor_Callback()

    def config_file_selected(self, index):
        """Callback function triggered when a folder is selected."""
        if index >= 0:  # Ensure a valid selection
            selected_folder = self.config_dropdown.itemText(index)
            selected_path = os.path.join(self.config_folder, selected_folder)
            print(f"Selected Experiment Folder: {selected_path}")

    def populate_config_dropdown(self):
        """Populates the dropdown with experiment folders."""
        if not os.path.exists(self.config_folder):
            print(f"Error: Config folder '{self.config_folder}' does not exist.")
            return

        # List subfolders (experiment folders)
        experiment_folders = [f for f in os.listdir(self.config_folder) if os.path.isdir(os.path.join(self.config_folder, f))]

        if not experiment_folders:
            print("No experiment folders found.")
            return

        # Add experiment folders to the dropdown
        self.config_dropdown.clear()  # Clear previous items
        self.config_dropdown.addItems(experiment_folders)

    def attempt_selected(self, index):
        self.attempt_info_label.show()
        if index >= 0:
            selected_attempt = self.attempts_dropdown.itemData(index)
            
            # This is an example of the data you can display (replace it with actual data from the attempt)
            attempt_data = f"Attempt {index+1} details:\n"
            attempt_data += f"Start: {selected_attempt['Start']}\n"
            attempt_data += f"End: {selected_attempt['Stop']}\n"
            attempt_data += f"Result: {selected_attempt['Result']}"

            # Update the label to show the corresponding data for the selected attempt
            self.attempt_info_label.setText(attempt_data)

    
class CountdownWidget(QWidget):

    timeout_signal = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()
        self.timer_label = QLabel(f"Remaining time: {params.remaining_time}")
        self.timer_label.setStyleSheet('color: #000066;')
        layout.addWidget(self.timer_label)
        self.setLayout(layout)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)

    def start_countdown(self):
        if params.CalibrationStage == 1:
            params.remaining_time = params.TimeCalibStage1
        if params.CalibrationStage == 2:
            params.remaining_time = params.TimeCalibStage2
        if params.CalibrationStage == 3:
            params.remaining_time = params.TimeCalibStage3

        self.remaining_time = params.remaining_time
        self.timer_label.setText(f"Remaining time: {self.remaining_time}")
        self.timer.start(1000)

    def update_timer(self):
        self.remaining_time -= 1
        if self.remaining_time >= 0:
            self.timer_label.setText(f"Remaining time: {self.remaining_time}")
        else:
            self.timer.stop()
            self.timer_label.setText("Timeout")
            self.timeout_signal.emit()
            params.CalibrationStageInitialized = False
            params.CalibrationStageFinished = True

class CalibrationWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Calibration Window")
        self.setGeometry(100, 100, 800, 600)
        self.CalibrationStage = 0

        # Disable the close (X) button
        self.setWindowFlag(Qt.WindowCloseButtonHint, False)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        self.setStyleSheet("background-color:#DDDDDD;")

        layout = QVBoxLayout()

        self.stage1_button = QPushButton("1 - Base Noise")
        self.stage1_button.setFixedSize(240, 30)  # Set a fixed size for the button
        self.stage1_button.setStyleSheet('QPushButton {color: #000066;}')

        self.stage2_button = QPushButton("2 - Maximum Activations")
        self.stage2_button.setFixedSize(240, 30)  # Set a fixed size for the button
        self.stage2_button.setStyleSheet('QPushButton {color: #000066;}')
        
        self.stage3_button = QPushButton("3 - Synergy Basis")
        self.stage3_button.setFixedSize(240, 30)  # Set a fixed size for the button
        self.stage3_button.setStyleSheet('QPushButton {color: #000066;}')
        
        self.upload_calibration_button = QPushButton("Upload Last Calibration")
        self.upload_calibration_button.setFixedSize(240, 30)  # Set a fixed size for the button
        self.upload_calibration_button.setStyleSheet('QPushButton {color: #000066;}')

        self.choose_projection_button = QPushButton("Choose Projection")
        self.choose_projection_button.setFixedSize(240, 30)  # Set a fixed size for the button
        self.choose_projection_button.setStyleSheet('QPushButton {color: #000066;}')
        
        self.terminate_button = QPushButton("Terminate Calibration")
        self.terminate_button.setFixedSize(240, 30)  # Set a fixed size for the button
        self.terminate_button.setStyleSheet('QPushButton {color: #000066;}')
        
        self.set_synergy_base = QPushButton("Set Synergies Basis")
        self.set_synergy_base.setFixedSize(240, 30)  # Set a fixed size for the button
        self.set_synergy_base.setStyleSheet('QPushButton {color: #000066;}')
        self.set_synergy_base.hide()

        self.synergies_lineedit_label = QLabel("Select the number of synergies:")
        self.synergies_lineedit_label.setStyleSheet('color: #000066;')
        self.synergy_base_lineedit = QLineEdit()
        self.synergy_base_lineedit.setFixedWidth(100)
        self.synergy_base_lineedit.hide()
        self.synergies_lineedit_label.hide()
        
        #self.stage_message_label = QLabel("")
        self.stage_message_label = QTextBrowser()
        self.stage_message_label.setStyleSheet('color: #000066;')
        self.stage_message_label.setFixedWidth(240)
        
        # Initialize Start buttons for each stage
        self.start_stage_button = QPushButton("Start")
        self.start_stage_button.setStyleSheet('QPushButton {color: #000066;}')
        self.start_stage_button.setFixedSize(240, 30)  # Set a fixed size for the button
        self.start_stage_button.hide()  # Initially hide the Start button
        
        self.sensors_dropdown = QComboBox(self)
        self.sensors_dropdown.setToolTip("Select a muscle to calibrate:")
        self.sensors_dropdown.setStyleSheet("QComboBox {color: #000066; background: #848482;}")
        self.sensors_dropdown.currentIndexChanged.connect(self.sensor_selected)
        self.sensors_dropdown.hide()
        self.sensors_dropdown_label = QTextBrowser()
        self.sensors_dropdown_label.hide()
        
        self.timer_widget = CountdownWidget()
        self.timer_widget.hide()  # Initially hide the CountdownWidget

        self.stage1_button.clicked.connect(self.stage1_callback)
        self.stage2_button.clicked.connect(self.stage2_callback)
        self.stage3_button.clicked.connect(self.stage3_callback)
        self.upload_calibration_button.clicked.connect(self.stage4_callback)
        self.choose_projection_button.clicked.connect(self.show_select_model)
        self.terminate_button.clicked.connect(self.terminate_callback)

        # Connect Start button to start countdown
        self.start_stage_button.clicked.connect(self.start_countdown)
        self.set_synergy_base.clicked.connect(self.set_model)

        self.figure = plt.figure() 
        self.canvas = FigureCanvas(self.figure)
        self.colors = ['Red', 'Blue', 'Yellow', 'Green', 'Orange', 'Purple', 'Grey', 'Brown']
        
        params.PlotCalibrationSignal.signal.connect(self.update_plot)

        # Angles selection window
        angles_layout = QVBoxLayout()

        self.angle_lineedits = []
        self.angle_labels = []
        for i in range(8):
            angle_label = QLabel(f"Synergy {i+1}:")
            angle_label.setStyleSheet('color: #000066;')
            angle_lineedit = QLineEdit()
            angle_lineedit.setFixedWidth(100)
            angle_lineedit.hide()
            angle_label.hide()
            self.angle_lineedits.append(angle_lineedit)
            self.angle_labels.append(angle_label)
            angles_layout.addWidget(angle_label)
            angles_layout.addWidget(angle_lineedit)
            # Connect the textChanged signal to the update_plot method
            angle_lineedit.textChanged.connect(self.update_plot)

        self.save_button = QPushButton("Save Angles")
        self.save_button.setFixedWidth(100)
        self.save_button.setStyleSheet('QPushButton {color: #000066;}')
        self.save_button.hide()
        self.save_button.clicked.connect(self.save_angles)

        angles_layout.addWidget(self.save_button)
        
        #Construct the layout 
        layout.addWidget(self.stage1_button)
        layout.addWidget(self.stage2_button)
        layout.addWidget(self.stage3_button)
        layout.addWidget(self.upload_calibration_button)
        layout.addWidget(self.choose_projection_button)
        layout.addWidget(self.stage_message_label)
        layout.addWidget(self.sensors_dropdown)
        layout.addWidget(self.start_stage_button)
        layout.addWidget(self.timer_widget)
        layout.addWidget(self.synergies_lineedit_label)
        layout.addWidget(self.synergy_base_lineedit)
        layout.addWidget(self.set_synergy_base)
        layout.addLayout(angles_layout)
        layout.addWidget(self.terminate_button)
        main_layout.addLayout(layout)
        main_layout.addWidget(self.canvas)
        main_layout.setStretch(1, 1)

    def stage1_callback(self):
        self.save_button.hide()
        for i in range(params.SynergiesNumber):
            self.angle_lineedits[i].hide()
            self.angle_labels[i].hide()
        self.synergies_lineedit_label.hide()
        self.synergy_base_lineedit.hide()
        self.set_synergy_base.hide()

        self.stage_message_label.show()
        self.start_stage_button.show()
        self.sensors_dropdown.show()
        
        self.stage_message_label.setText("Calibration Stage 1: Activation Threshold Detection \nHold as still as possible to detect the baseline noise of each sensor. Try not to activate any muscles during the countdown.")
        
        self.populate_sensors_dropdown()
        self.CalibrationStage = 1
      

    def stage2_callback(self):
        self.save_button.hide()
        for i in range(params.SynergiesNumber):
            self.angle_lineedits[i].hide()
            self.angle_labels[i].hide()
        self.synergies_lineedit_label.hide()
        self.synergy_base_lineedit.hide()
        self.set_synergy_base.hide()

        self.stage_message_label.show()
        self.start_stage_button.show()
        self.sensors_dropdown.show()

        self.stage_message_label.setText("Calibration Stage 2: Activation Peaks Detection \nTry to activate each muscle to its maximum during the countdown to determine the maximum activation.")
       
        self.populate_sensors_dropdown()
        self.CalibrationStage = 2
        

    def stage3_callback(self):
        self.save_button.hide()
        for i in range(params.SynergiesNumber):
            self.angle_lineedits[i].hide()
            self.angle_labels[i].hide()
        self.synergies_lineedit_label.hide()
        self.synergy_base_lineedit.hide()
        self.set_synergy_base.hide()
        self.sensors_dropdown.hide()

        self.stage_message_label.show()
        self.start_stage_button.show()
        
        self.stage_message_label.setText("Calibration Stage 3: Synergies Detection \nIn this stage, muscle synergies will be detected. During the countdown, try to activate all the involved muscles with random movements.")
      
        self.CalibrationStage = 3
        

    def stage4_callback(self):
        for i in range(params.SynergiesNumber):
            self.angle_lineedits[i].hide()
            self.angle_labels[i].hide()
        self.save_button.hide()
        self.synergies_lineedit_label.hide()
        self.synergy_base_lineedit.hide()
        self.set_synergy_base.hide()
        self.sensors_dropdown.hide()

        self.stage_message_label.show()
        self.start_stage_button.show()
        
        self.stage_message_label.setText("Press Start to upload the calibration from the Configuration.json file located in the root of the project.")
        
        self.CalibrationStage = 4
        

    def start_countdown(self):
        print("timer")
        # Show the countdown widget and start the countdown
        params.CalibrationStage = self.CalibrationStage
        params.CalibrationStageInitialized = True
        if self.CalibrationStage == 4:
            pass
        else:
            self.timer_widget.timer_label.show()
            self.timer_widget.show()
            self.timer_widget.start_countdown()
    
    def sensor_selected(self, index):
        if index >= 0:
            selected_sensor = self.sensors_dropdown.itemText(index)
            params.selectedSensorIndex = index
            

    def populate_sensors_dropdown(self):
        self.sensors_dropdown.clear()
        self.sensors_dropdown.addItems(['All'])
        self.sensors_dropdown.addItems(params.SensorStickers)

    def terminate_callback (self):
        params.TerminateCalibrationFlag = True
        # try:
        #     params.SaveCalibrationToJson(
        #                                         params.ChannelsNumber,
        #                                         params.Thresholds,
        #                                         params.Peaks,
        #                                         params.AnglesOutput,
        #                                         params.SynergyBase,
        #                                         params.SensorStickers
        #                                         )
        # except Exception as e:
        #     msgbox.alert(e)
        self.close()

    def show_select_model(self):
        self.start_stage_button.hide()
        self.stage_message_label.hide()
        self.sensors_dropdown.hide()
        self.timer_widget.timer_label.hide()

        params.CalibrationStage = 6
        
        self.synergies_lineedit_label.show()
        self.synergy_base_lineedit.show()
        self.set_synergy_base.show()

        params.PlotModels = True
        try:
            self.update_plot()
        except Exception as e:
            msgbox.alert(e)

        
        
    def show_angle_window(self):
        self.save_button.show()
        params.AnglesOutput = []
        # Show the AngleWindow only in stage 3
        for i in range(params.SynergiesNumber):
            self.angle_lineedits[i].show()
            self.angle_labels[i].show()
        params.PlotAngles = True
        self.update_plot()

    def update_plot(self):

        if params.PlotThresholds:
            self.figure.clear()
            ax = self.figure.add_subplot(111)
            data = params.Thresholds 
            ax.bar(params.SensorStickers, data, color = "#1A4207")
            # If any data values is more than .1, color it red
            for i, value in enumerate(data):
                if value > 0.1:
                    ax.bar(params.SensorStickers[i], value, color = "#B11E1E")
                # If any data value is between .08 and .1, color it orange
                elif 0.08 < value <= 0.1:
                    ax.bar(params.SensorStickers[i], value, color = "#B46A0F")
            ax.set_xlabel('Muscles')  # X-axis label
            ax.set_ylabel('Muscle Activation (mV)')  # Y-axis label
            ax.set_title('Detected thresholds')  # Plot title
            params.PlotThresholds = False
            
                
        elif params.PlotPeaks:
            self.figure.clear()
            ax = self.figure.add_subplot(111)
            data = params.Peaks 
            ax.bar(params.SensorStickers, data, color = "#1A4207")
            #If any data value is less than .5, color it red
            for i, value in enumerate(data):
                if value < 0.3:
                    ax.bar(params.SensorStickers[i], value, color = "#B11E1E")
                elif 0.3 <= value < 0.5:
                    ax.bar(params.SensorStickers[i], value, color = "#B46A0F")
            # Add bars with current thresholds overlaid on top of the peaks
            thresholds = params.Thresholds
            ax.bar(params.SensorStickers, thresholds, color = "#3B6CF3")
            ax.set_xlabel('Muscles')  # X-axis label
            ax.set_ylabel('Muscle Activation (mV)')  # Y-axis label
            ax.set_title('Detected Peaks')  # Plot title
            params.PlotPeaks = False

        elif params.PlotModels:
            self.figure.clear()            
            data = params.SynergiesModels
            gs = self.figure.add_gridspec(params.ChannelsNumber + 1, params.ChannelsNumber - 1)  

            subplots = []
            for j in range(2, params.ChannelsNumber + 1):
                for i in range (1, j+1):
                    ax = self.figure.add_subplot(gs[i-1, j-2])
                    ax.bar([str(index) for index in range(1, params.ChannelsNumber + 1)], data[f'{j} Synergies'][i-1], color='#00008B', alpha=0.6)
                    subplots.append(ax)
                    ax.set_ylim(0, 1)  # Set y-axis limits to be between 0 and 0.5
                    ax.set_xlim(-0.5, params.ChannelsNumber-0.5) 
                    ax.set_xticks(range(params.ChannelsNumber))  # Ensure all ticks are visible
                    ax.set_yticks([0, 0.5, 1])  # Ensure y-ticks are visible
                    if i == 1:
                        ax.set_title(f'{j} Synergies')
                        if j == 2:
                            ax.set_xlabel('Muscles')  # X-axis label
                            ax.set_ylabel('Relative Activation')  # Y-axis label
                            ax.set_xticklabels(params.SensorStickers)
                            ax.set_yticklabels([str(tick) for tick in [0, 0.5, 1]])
                        else:
                            ax.set_xticklabels([''] * params.ChannelsNumber)  # Remove x-axis tick labels but keep the ticks
                            ax.set_yticklabels([''] * 3)  # Remove y-axis tick labels but keep the ticks
                    else:
                        ax.set_xticklabels([''] * params.ChannelsNumber)  # Remove x-axis tick labels but keep the ticks
                        ax.set_yticklabels([''] * 3)  # Remove y-axis tick labels but keep the ticks
                            
            ax = self.figure.add_subplot(gs[params.ChannelsNumber , 0])
            x = list(range(2, params.ChannelsNumber+1))  # Number of muscles
            ax.plot(x, data['vafs'], marker='o', label='VAF Curve')
            ax.set_xlabel('Number of Synergies')
            ax.set_ylabel('VAF (%)')
            ax.set_title('VAF vs Model')

            # Ensure the x-axis contains only integers
            ax.set_xticks(np.arange(2, params.ChannelsNumber + 1, 1))  # Set x-ticks from 2 to the number of channels
            ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: '{:d}'.format(int(x))))  # Ensure x-ticks are displayed as integers

            # Adjust the layout to expand subplots
            self.figure.tight_layout()
            self.figure.subplots_adjust(hspace=0.8, wspace=0.6)  # Adjust the spacing if needed

            params.PlotModels = False
            
        elif params.PlotAngles:
            self.figure.clear()
            try:
                angles = [lineedit.text() for lineedit in self.angle_lineedits]
                try:
                    angles = [int(angle) for angle in angles if angle]
                except ValueError:
                    return  # Ignore invalid input
                
                gs = self.figure.add_gridspec(params.SynergiesNumber, 2)  
                # Plot Synergy Base ----------------------------------------------
                for i in range (1, params.SynergiesNumber+1):
                    ax = self.figure.add_subplot(gs[i-1, 0])
                    ax.bar(range(np.asarray(params.SynergyBase).shape[1]), params.SynergyBase[i-1], color=self.colors[i-1], alpha=0.6)
                    ax.set_ylim(0, 1)  # Set y-axis limits to be between 0 and 0.5
                    ax.set_xlim(-0.5, params.ChannelsNumber-0.5)  
                    ax.set_xticks(range(params.ChannelsNumber))  # Ensure all ticks are visible
                    ax.set_yticks([0, 0.5, 1])  # Ensure y-ticks are visible

                    if i == 1:
                        ax.set_title(f'Synergy Basis ({params.SynergiesNumber} Synergies)')
                        ax.set_xlabel('Muscles')  # X-axis label
                        ax.set_ylabel('Reltive Activation')  # Y-axis label
                        ax.set_xticklabels(params.SensorStickers)
                        ax.set_yticklabels([str(tick) for tick in [0, 0.5, 1]])
                    else: 
                        ax.set_xticklabels([''] * params.ChannelsNumber)  # Remove x-axis tick labels but keep the ticks
                        ax.set_yticklabels([''] * 3)  # Remove y-axis tick labels but keep the ticks
            except Exception as e:
                msgbox.alert(e)   
            # Plot Projection Angles ----------------------------------------------
            ax = self.figure.add_subplot(gs[:, 1], polar=True)
            ax.set_title("Choose the projection angle of each synergy")
            for i in range(len(angles)):
                theta = np.radians(angles[i])  # Convert to radians
                ax.plot([0, theta], [0, 1], marker='o', color=self.colors[i])  # Plot the vector
            
            # Adjust the layout to expand subplots
            self.figure.tight_layout()
            self.figure.subplots_adjust(hspace=0.8, wspace=0.6)  # Adjust the spacing if needed

        elif params.PlotUploadedConfig:
            self.figure.clear()
            gs = self.figure.add_gridspec(params.SynergiesNumber, 2)  
            
            # Plot Synergy Base ----------------------------------------------
            for i in range (1, params.SynergiesNumber+1):
                ax = self.figure.add_subplot(gs[i-1, 0])
                ax.bar(range(np.asarray(params.SynergyBase).shape[1]), params.SynergyBase[i-1], color=self.colors[i-1], alpha=0.6)
                ax.set_ylim(0, 1)  # Set y-axis limits to be between 0 and 0.5
                ax.set_xlim(-0.5, params.ChannelsNumber-0.5) 
                ax.set_xticks(range(params.ChannelsNumber))  # Ensure all ticks are visible
                ax.set_yticks([0, 0.5, 1])  # Ensure y-ticks are visible

                if i == 1:
                    ax.set_title(f'Synergy Basis ({params.SynergiesNumber} Synergies)')
                    ax.set_xlabel('Muscles')  # X-axis label
                    ax.set_ylabel('Relative Activation')  # Y-axis label
                    ax.set_xticklabels(params.SensorStickers)
                    ax.set_yticklabels([str(tick) for tick in [0, 0.5, 1]])
                else: 
                    ax.set_xticklabels([''] * params.ChannelsNumber)  # Remove x-axis tick labels but keep the ticks
                    ax.set_yticklabels([''] * 3)  # Remove y-axis tick labels but keep the ticks
                
            # Plot Projection Angles ----------------------------------------------
            ax = self.figure.add_subplot(gs[:, 1], polar=True)
            ax.set_title("Projection Angles")
            for i in range(len(params.AnglesOutput)):
                theta = np.radians(int(params.AnglesOutput[i]))  # Convert to radians
                ax.plot([0, theta], [0, 1], marker='o', color=self.colors[i])  # Plot the vector
            
            # Adjust the layout to expand subplots
            self.figure.tight_layout()
            self.figure.subplots_adjust(hspace=0.8, wspace=0.6)  # Adjust the spacing if needed
            params.PlotUploadedConfig = False
            
        else:
            print("Invalid Plot Mode")

        self.canvas.draw()
    
    def set_model(self):
        self.SynergiesNumber = int(self.synergy_base_lineedit.text())
        if self.SynergiesNumber >= 2 and self.SynergiesNumber <= params.ChannelsNumber:
            params.SynergiesNumber = self.SynergiesNumber
            params.SynergyBase = params.SynergiesModels[f'{self.SynergiesNumber} Synergies']
            self.show_angle_window()
           
        else: 
            msgbox.alert("Invalid number of synegies. Close this window and choose the number of synergies again.")

    def save_angles(self):
        AnglesOutput = []
        AnglesCount = 0
        angles = [lineedit.text() for lineedit in self.angle_lineedits]
        for angle in angles:
            if angle != '':
                AnglesCount = AnglesCount + 1
                AnglesOutput.append(angle)
        if AnglesCount != params.SynergiesNumber:
            msgbox.alert("The number of angles doesn't match with the number of synegies selected. Choose the angles again.")
            self.show_angle_window()
        else:
            params.PlotAngles = False
            params.AnglesOutputSemaphore.acquire()
            params.AnglesReady = 1
            params.AnglesOutput = AnglesOutput
            params.AnglesOutputSemaphore.release()
           
            

if __name__ == '__main__':
    app = QApplication(sys.argv)
    CollectDataWindow = CollectDataWindow()
    CollectDataWindow.show()
    sys.exit(app.exec_())



