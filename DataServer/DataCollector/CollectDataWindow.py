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
import csv
import numpy as np
import time



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
    
    def is_data_empty(self, data):
        """Safely check if data is empty, handling both lists and numpy arrays"""
        if data is None:
            return True
        
        try:
            if isinstance(data, np.ndarray):
                return data.size == 0
            elif hasattr(data, '__len__'):
                return len(data) == 0
            else:
                return not bool(data)
        except Exception as e:
            print(f"[WARNING] Error checking data emptiness: {e}")
            return True
    
    def get_data_length(self, data):
        """Safely get the length of data, handling both lists and numpy arrays"""
        if data is None:
            return 0
        
        try:
            if isinstance(data, np.ndarray):
                return data.size
            elif hasattr(data, '__len__'):
                return len(data)
            else:
                return 1 if data else 0
        except Exception as e:
            print(f"[WARNING] Error getting data length: {e}")
            return 0
    
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

        connect_layout = QHBoxLayout()
        
        #---- Connect Base Button
        self.connect_base_button = QPushButton('Connect Base', self)
        self.connect_base_button.setToolTip('Connect to Delsys Base')
        self.connect_base_button.setSizePolicy(QSizePolicy.Preferred,QSizePolicy.Expanding)
        self.connect_base_button.objectName = 'Connect Base'
        self.connect_base_button.clicked.connect(self.connect_base_callback)
        self.connect_base_button.setStyleSheet('QPushButton {background-color: #4CAF50; color: #FFFFFF;}')
        self.connect_base_button.setEnabled(True)
        connect_layout.addWidget(self.connect_base_button)

        #---- Connect From File Button
        self.connect_file_button = QPushButton('Connect From File', self)
        self.connect_file_button.setToolTip('Connect using CSV file')
        self.connect_file_button.setSizePolicy(QSizePolicy.Preferred,QSizePolicy.Expanding)
        self.connect_file_button.objectName = 'Connect From File'
        self.connect_file_button.clicked.connect(self.connect_file_callback)
        self.connect_file_button.setStyleSheet('QPushButton {color: #000066;}')
        connect_layout.addWidget(self.connect_file_button)

        buttonLayout.addLayout(connect_layout)

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
        # Always append connection type if connected
        if hasattr(params, 'DelsysMode'):
            if params.DelsysMode is True:
                self.pipelinestatelabel.setText(self.pipelinetext + " (Base)")
            elif params.DelsysMode is False:
                self.pipelinestatelabel.setText(self.pipelinetext + " (File)")
        else:
            self.pipelinestatelabel.setText(self.pipelinetext)

    def connect_base_callback(self):
        params.DelsysMode = True
        try:
            self.CallbackConnector.Connect_Callback()
            # If connection successful, disable both buttons and enable scan
            self.connect_base_button.setEnabled(False)
            self.connect_file_button.setEnabled(False)
            self.scan_button.setEnabled(True)
            self.getpipelinestate()
            self.pipelinestatelabel.setText(self.pipelinetext + " (Base Connected)")
        except Exception as e:
            # Handle connection error gracefully
            msgbox.alert(f"Failed to connect to Delsys base:\n{str(e)}\n\nPlease check that:\n"
                        "- The base is powered on and connected\n"
                        "- Drivers are properly installed\n"
                        "- No other application is using the base")
            
            # Reset the connection state to allow user to try again
            self.reset_connection_state()

    def connect_file_callback(self):
        # Create a hidden tkinter root to prevent blank window
        root = tk.Tk()
        root.withdraw()  # Hide the main tkinter window
        
        # Open file dialog to select CSV file
        file_path = filedialog.askopenfilename(
            title="Select a CSV file containing muscle data to simulate connection",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
        )
        
        # Destroy the tkinter root to clean up
        root.destroy()
        
        if file_path:
            # Validate the CSV file
            if self.validate_csv_file(file_path):
                params.DelsysMode = False
                params.csvFile = file_path
                try:
                    self.CallbackConnector.Connect_Callback()
                    # If connection successful, disable both buttons and enable scan
                    self.connect_base_button.setEnabled(False)
                    self.connect_file_button.setEnabled(False)
                    self.scan_button.setEnabled(True)
                    self.getpipelinestate()
                    self.pipelinestatelabel.setText(self.pipelinetext + " (File Connected)")
                except Exception as e:
                    # Handle connection error gracefully
                    msgbox.alert(f"Failed to connect using CSV file:\n{str(e)}\n\nPlease try selecting a different file.")
                    self.reset_connection_state()
            # Note: Error details are now provided by validate_csv_file method

    def validate_csv_file(self, file_path):
        """Validate that the CSV file has the expected format"""
        try:
            import csv
            with open(file_path, 'r') as file:
                csv_reader = csv.reader(file, delimiter=',')
                
                # Read header row
                try:
                    header = next(csv_reader)
                    if len(header) < 2:  # At least timestamp + one data column
                        msgbox.alert(f"CSV file error: Header row has only {len(header)} column(s).\n"
                                   f"Expected at least 2 columns (timestamp + data columns).\n"
                                   f"Header found: {header}")
                        return False
                    header_col_count = len(header)
                except StopIteration:
                    msgbox.alert("CSV file error: File appears to be empty (no header row found).")
                    return False
                
                # Check data rows
                row_count = 0
                for row_num, row in enumerate(csv_reader, start=2):  # Start at 2 since header is row 1
                    if len(row) != header_col_count:
                        msgbox.alert(f"CSV file error: Row {row_num} has {len(row)} columns, "
                                   f"but header has {header_col_count} columns.\n"
                                   f"All rows must have the same number of columns.\n"
                                   f"Problem row: {row[:5]}{'...' if len(row) > 5 else ''}")
                        return False
                    
                    # Skip first column (timestamp), check remaining are numeric
                    for col_idx, value in enumerate(row[1:], start=1):
                        try:
                            float(value)
                        except ValueError:
                            col_name = header[col_idx] if col_idx < len(header) else f"Column {col_idx + 1}"
                            msgbox.alert(f"CSV file error: Non-numeric value found in row {row_num}, column '{col_name}'.\n"
                                       f"Value: '{value}'\n"
                                       f"All data columns (except the first one) must contain numeric values.\n"
                                       f"First column (timestamp) can be any value and will be ignored.")
                            return False
                    
                    row_count += 1
                    if row_count > 10:  # Check first 10 rows for performance
                        break
                
                if row_count == 0:
                    msgbox.alert("CSV file error: No data rows found after the header.\n"
                               "File must contain at least one row of data.")
                    return False
                
                return True
                
        except FileNotFoundError:
            msgbox.alert(f"CSV file error: Could not find file at path:\n{file_path}")
            return False
        except PermissionError:
            msgbox.alert(f"CSV file error: Permission denied when trying to read file:\n{file_path}\n"
                       "Please check that the file is not open in another application.")
            return False
        except Exception as e:
            msgbox.alert(f"CSV file error: Unexpected error while reading file:\n{str(e)}")
            return False

    def reset_connection_state(self):
        """Reset the UI to allow user to try connecting again"""
        self.connect_base_button.setEnabled(True)
        self.connect_file_button.setEnabled(True)
        self.scan_button.setEnabled(False)
        self.calibration_button.setEnabled(False)
        self.cursor_button.setEnabled(False)
        self.visualization_button.setEnabled(False)
        self.getpipelinestate()
        self.pipelinestatelabel.setText("Connection Failed - Ready to Retry")

    def connect_callback(self):
        # Legacy method for backward compatibility
        self.connect_base_callback()

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

    def plot_synergy_and_calibration_data(self):
        """Plot synergy basis, projection angles, and thresholds/peaks data"""
        self.figure.clear()
        self.synergiesNumber = np.array(self.synergy_base).shape[0]
        gs = self.figure.add_gridspec(self.synergiesNumber + 1, 2)  # Added +1 for the new plot
        
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
        ax = self.figure.add_subplot(gs[:self.synergiesNumber, 1], polar=True)
        ax.set_title("Projection Angles")
        for i in range(len(self.angles)):
            theta = np.radians(int(self.angles[i]))  # Convert to radians
            ax.plot([0, theta], [0, 1], marker='o', color=self.colors[i])  # Plot the vector
        
        # Plot Thresholds and Peaks ----------------------------------------------
        ax = self.figure.add_subplot(gs[self.synergiesNumber, :])
        x_positions = range(len(self.sensor_stickers))
        width = 0.35
        
        # Plot thresholds
        ax.bar([x - width/2 for x in x_positions], self.thresholds, width, 
               label='Thresholds', color='blue', alpha=0.7)
        
        # Plot peaks
        ax.bar([x + width/2 for x in x_positions], self.peaks, width, 
               label='Peaks', color='red', alpha=0.7)
        
        ax.set_xlabel('Muscles')
        ax.set_ylabel('Muscle Activation (mV)')
        ax.set_title('Thresholds and Peaks')
        ax.set_xticks(x_positions)
        ax.set_xticklabels(self.sensor_stickers)
        ax.legend()
        
        # Adjust the layout to expand subplots
        self.figure.tight_layout()
        self.figure.subplots_adjust(hspace=0.8, wspace=0.6)  # Adjust the spacing if needed
        self.canvas.draw()

    def plot_data(self):
        self.plot_synergy_and_calibration_data()

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

        self.upload_configuration_button = QPushButton("Upload configuration")
        self.upload_configuration_button.setFixedSize(240, 30)  # Set a fixed size for the button
        self.upload_configuration_button.setStyleSheet('QPushButton {color: #000066;}')
        
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
        self.terminate_button.clicked.connect(self.terminate_callback)

        # Connect Start button to start countdown
        self.start_stage_button.clicked.connect(self.start_countdown)
        self.set_synergy_base.clicked.connect(self.set_model)

        self.figure = plt.figure() 
        self.canvas = FigureCanvas(self.figure)
        self.colors = ['Red', 'Blue', 'Yellow', 'Green', 'Orange', 'Purple', 'Grey', 'Brown']
        
        params.PlotCalibrationSignal.signal.connect(self.update_plot_with_debug)

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
        import DataServer.API_Parameters as params
        from General.utils import check_calibration_json
        from tkinter import Tk, filedialog
        import pymsgbox

        self.stage_message_label.setText("Select a calibration JSON file to upload.")

        # Prompt user to select a file
        while True:
            root = Tk()
            root.withdraw()
            file_path = filedialog.askopenfilename(title="Select Calibration JSON", filetypes=[("JSON files", "*.json")])
            root.destroy()
            if not file_path:
                pymsgbox.alert("No file selected. Calibration upload cancelled.")
                return
            # Check the file
            if check_calibration_json(file_path, params.SensorStickers):
                params.CalibrationJsonPath = file_path
                self.stage_message_label.setText("Calibration file accepted successfully. Ready to load.")
                break
            else:
                retry = pymsgbox.confirm("Selected file failed validation. Try another file?", "Calibration Error", ["Try Again", "Cancel"])
                if retry != "Try Again":
                    pymsgbox.alert("Calibration upload cancelled.")
                    return
        # Hide GUI elements as before
        for i in range(params.SynergiesNumber):
            self.angle_lineedits[i].hide()
            self.angle_labels[i].hide()
        self.save_button.hide()
        self.synergies_lineedit_label.hide()
        self.synergy_base_lineedit.hide()
        self.set_synergy_base.hide()
        self.sensors_dropdown.hide()
        self.stage_message_label.show()
        self.start_stage_button.text = "Load Calibration"
        self.start_stage_button.show()
        self.CalibrationStage = 4

    def start_countdown(self):
        print("timer")
        # Show the countdown widget and start the countdown
        params.CalibrationStage = self.CalibrationStage
        params.CalibrationStageInitialized = True
        if self.CalibrationStage == 4:
            self.start_stage_button.hide()
            self.timer_widget.timer_label.hide()
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
            print("[DEBUG] Calling update_plot from show_select_model")
            self.update_plot()
        except Exception as e:
            print(f"[ERROR] Error in show_select_model: {e}")
            msgbox.alert(f"Error displaying synergy models: {str(e)}")

    def show_angle_window(self):
        self.save_button.show()
        params.AnglesOutput = []
        # Show the AngleWindow only in stage 3
        for i in range(params.SynergiesNumber):
            self.angle_lineedits[i].show()
            self.angle_labels[i].show()
        params.PlotAngles = True
        try:
            print("[DEBUG] Calling update_plot from show_angle_window")
            self.update_plot()
        except Exception as e:
            print(f"[ERROR] Error in show_angle_window: {e}")
            msgbox.alert(f"Error displaying angle selection: {str(e)}")

    def update_plot(self):
        if params.PlotThresholds:
        #     self.figure.clear()
        #     ax = self.figure.add_subplot(111)
        #     data = np.array(params.Thresholds) 
        #     ax.bar(params.SensorStickers, data, color = '#00008B')
        #     ax.set_xlabel('Muscles')  # X-axis label
        #     ax.set_ylabel('Muscle Activation (mV)')  # Y-axis label
        #     ax.set_title('Detected thresholds')  # Plot title
        #     params.PlotThresholds = False
                
        # elif params.PlotPeaks:
        #     self.figure.clear()
        #     ax = self.figure.add_subplot(111)
        #     # data = params.Peaks
        #     data = np.array(params.Peaks)  # Ensure data is in a suitable format for plotting 
        #     ax.bar(params.SensorStickers, data, color = '#00008B')
        #     ax.set_xlabel('Muscles')  # X-axis label
        #     ax.set_ylabel('Muscle Activation (mV)')  # Y-axis label
        #     ax.set_title('Detected Peaks')  # Plot title
        
            self.plot_config()
            params.PlotPeaks = False

        elif params.PlotModels:
            # self.figure.clear()            
            # data = params.SynergiesModels
            # gs = self.figure.add_gridspec(params.ChannelsNumber + 1, params.ChannelsNumber - 1)  

            # subplots = []
            # for j in range(2, params.ChannelsNumber + 1):
            #     for i in range (1, j+1):
            #         ax = self.figure.add_subplot(gs[i-1, j-2])
            #         ax.bar([str(index) for index in range(1, params.ChannelsNumber + 1)], data[f'{j} Synergies'][i-1], color='#00008B', alpha=0.6)
            #         subplots.append(ax)
            #         ax.set_ylim(0, 1)  # Set y-axis limits to be between 0 and 0.5
            #         ax.set_xlim(-0.5, params.ChannelsNumber-0.5) 
            #         ax.set_xticks(range(params.ChannelsNumber))  # Ensure all ticks are visible
            #         ax.set_yticks([0, 0.5, 1])  # Ensure y-ticks are visible
            #         if i == 1:
            #             ax.set_title(f'{j} Synergies')
            #             if j == 2:
            #                 ax.set_xlabel('Muscles')  # X-axis label
            #                 ax.set_ylabel('Relative Activation')  # Y-axis label
            #                 ax.set_xticklabels(params.SensorStickers)
            #                 ax.set_yticklabels([str(tick) for tick in [0, 0.5, 1]])
            #             else:
            #                 ax.set_xticklabels([''] * params.ChannelsNumber)  # Remove x-axis tick labels but keep the ticks
            #                 ax.set_yticklabels([''] * 3)  # Remove y-axis tick labels but keep the ticks
            #         else:
            #             ax.set_xticklabels([''] * params.ChannelsNumber)  # Remove x-axis tick labels but keep the ticks
            #             ax.set_yticklabels([''] * 3)  # Remove y-axis tick labels but keep the ticks
                            
            # ax = self.figure.add_subplot(gs[params.ChannelsNumber , 0])
            # x = list(range(2, params.ChannelsNumber+1))  # Number of muscles
            # ax.plot(x, data['vafs'], marker='o', label='VAF Curve')
            # ax.set_xlabel('Number of Synergies')
            # ax.set_ylabel('VAF (%)')
            # ax.set_title('VAF vs Model')

            # # Ensure the x-axis contains only integers
            # ax.set_xticks(np.arange(2, params.ChannelsNumber + 1, 1))  # Set x-ticks from 2 to the number of channels
            # ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: '{:d}'.format(int(x))))  # Ensure x-ticks are displayed as integers

            # # Adjust the layout to expand subplots
            # self.figure.tight_layout()
            # self.figure.subplots_adjust(hspace=0.8, wspace=0.6)  # Adjust the spacing if needed
            self.plot_config()
            params.PlotModels = False
            
        elif params.PlotAngles:
            self.figure.clear()
            try:
                angles = [lineedit.text() for lineedit in self.angle_lineedits]
                try:
                    self.figure.clear()
                    
                    # Check if SynergyBase data exists
                    synergy_base_available = False
                    if params.SynergyBase is not None:
                        if isinstance(params.SynergyBase, np.ndarray):
                            synergy_base_available = params.SynergyBase.size > 0
                        elif hasattr(params.SynergyBase, '__len__'):
                            synergy_base_available = len(params.SynergyBase) > 0
                        else:
                            synergy_base_available = bool(params.SynergyBase)
                    
                    if not synergy_base_available:
                        print("[ERROR] SynergyBase data is empty or None")
                        msgbox.alert("Cannot plot uploaded config: No synergy base data available")
                        return
                        
                    # Check if AnglesOutput data exists
                    if self.is_data_empty(params.AnglesOutput):
                        print("[ERROR] AnglesOutput data is empty or None")
                        msgbox.alert("Cannot plot uploaded config: No angles data available")
                        return
                    
                    gs = self.figure.add_gridspec(params.SynergiesNumber, 2)  
                    
                    # Plot Synergy Base ----------------------------------------------
                    for i in range (1, params.SynergiesNumber+1):
                        try:
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
                                if params.SensorStickers:
                                    ax.set_xticklabels(params.SensorStickers)
                                ax.set_yticklabels([str(tick) for tick in [0, 0.5, 1]])
                            else: 
                                ax.set_xticklabels([''] * params.ChannelsNumber)  # Remove x-axis tick labels but keep the ticks
                                ax.set_yticklabels([''] * 3)  # Remove y-axis tick labels but keep the ticks
                        except Exception as subplot_error:
                            print(f"[ERROR] Failed to create config subplot {i}: {subplot_error}")
                            continue
                        
                    # Plot Projection Angles ----------------------------------------------
                    try:
                        ax = self.figure.add_subplot(gs[:, 1], polar=True)
                        ax.set_title("Projection Angles")
                        for i in range(len(params.AnglesOutput)):
                            theta = np.radians(int(params.AnglesOutput[i]))  # Convert to radians
                            ax.plot([0, theta], [0, 1], marker='o', color=self.colors[i])  # Plot the vector
                    except Exception as angles_error:
                        print(f"[ERROR] Failed to plot projection angles: {angles_error}")
                    
                    # Adjust the layout to expand subplots
                    self.figure.tight_layout()
                    self.figure.subplots_adjust(hspace=0.8, wspace=0.6)  # Adjust the spacing if needed
                    self.canvas.draw()
                    print("[DEBUG] Uploaded config plot completed successfully")
                    params.PlotUploadedConfig = False
                    
                except Exception as e:
                    print(f"[ERROR] Failed to plot uploaded config: {e}")
                    msgbox.alert(f"Failed to plot uploaded config: {str(e)}")
                    params.PlotUploadedConfig = False
                    
            except Exception as e:
                print(f"[ERROR] Error in update_plot for angles: {e}")
                msgbox.alert(f"Error updating plot for angles: {str(e)}")
                params.PlotAngles = False

        elif params.PlotUploadedConfig:
            self.plot_config()
            params.PlotUploadedConfig = False
            
        else:
            print("Invalid Plot Mode")

        self.canvas.draw()
    
    def update_plot_with_debug(self):
        """Debug wrapper for update_plot called by signal"""
        print("[DEBUG] update_plot_with_debug() called via signal")
        print(f"[DEBUG] Signal triggered - PlotThresholds: {params.PlotThresholds}")
        print(f"[DEBUG] Signal triggered - PlotPeaks: {params.PlotPeaks}")
        print(f"[DEBUG] Signal triggered - PlotModels: {params.PlotModels}")
        try:
            self.update_plot()
        except Exception as e:
            print(f"[ERROR] Error in signal-triggered update_plot: {e}")
            msgbox.alert(f"Error updating plot via signal: {str(e)}")
    
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

    def plot_config(self):
        self.figure.clear()
        gs = self.figure.add_gridspec(params.SynergiesNumber + 1, 2)  # Added +1 for the new plot
        
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
        ax = self.figure.add_subplot(gs[:params.SynergiesNumber, 1], polar=True)
        ax.set_title("Projection Angles")
        for i in range(len(params.AnglesOutput)):
            theta = np.radians(int(params.AnglesOutput[i]))  # Convert to radians
            ax.plot([0, theta], [0, 1], marker='o', color=self.colors[i])  # Plot the vector
        
        # Plot Thresholds and Peaks ----------------------------------------------
        ax = self.figure.add_subplot(gs[params.SynergiesNumber, :])
        x_positions = range(len(params.SensorStickers))
        width = 0.35
        
        # Plot thresholds
        ax.bar([x - width/2 for x in x_positions], params.Thresholds, width, 
               label='Thresholds', color='blue', alpha=0.7)
        
        # Plot peaks
        ax.bar([x + width/2 for x in x_positions], params.Peaks, width, 
               label='Peaks', color='red', alpha=0.7)
        
        ax.set_xlabel('Muscles')
        ax.set_ylabel('Muscle Activation (mV)')
        ax.set_title('Thresholds and Peaks')
        ax.set_xticks(x_positions)
        ax.set_xticklabels(params.SensorStickers)
        ax.legend()
        
        # Adjust the layout to expand subplots
        self.figure.tight_layout()
        self.figure.subplots_adjust(hspace=0.8, wspace=0.6)  # Adjust the spacing if needed
            

if __name__ == '__main__':
    app = QApplication(sys.argv)
    CollectDataWindow = CollectDataWindow()
    CollectDataWindow.show()
    sys.exit(app.exec_())



