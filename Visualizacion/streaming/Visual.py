from bokeh.plotting import figure
from bokeh.models import LinearAxis, Range1d, HoverTool, ColumnDataSource, Legend
from bokeh.layouts import gridplot, column, row
from bokeh.models.widgets import CheckboxGroup, Div
from bokeh.io import curdoc
from tornado import gen
import numpy as np
import VisualizationParameters as params
import pymsgbox as msgbox
import time 
class Visual:
    def __init__(self, callbackFunc, running):
        self.text1 = Div(text="""<h1 style=color:blue">Visualizacion de musculos y sinergias</h1>""", width=900, height=25) # Text to be displayed at the top of the webpage
        self.EmptyContainerTitle = Div(text="""<h1 style="color:blue"></h1>""", width=900, height=20) # Empty container to create space between the text and checkboxes
        self.EmptyContainerLeft = Div(text="""<h1 style="color:blue"></h1>""", width=10, height=1000) # Empty container to create space between the checkboxes and the graphs
        self.running = running # Store the current state of the Flag
        self.callbackFunc = callbackFunc # Store the callback function
        self.hover = HoverTool(  # To show tooltip when the mouse hovers over the plot data        
                tooltips=[
                    ("index", "$index"), # Show index of plot data points
                    ("(x,y)", "(@x, $y)") # Show x and y coordinates of the plot data points
                ]
            )
        self.tools = "pan,box_zoom,wheel_zoom,reset" # Set pan, zoom, etc., options for the plot
        
        self.MusclesNumber = params.MusclesNumber
        self.SynergiesNumber = params.SynergiesNumber
        self.yAxisMax = 10.0
        self.colors = ["firebrick", "indigo", "green", "blue", "orange", "purple", "brown", "pink"]
        self.sampleRate = params.SampleRate
        self.timeStep = 1/self.sampleRate
        self.seconds = 4
        self.points2Display = int(self.seconds*self.sampleRate)
        self.MusclesStart = time.time()
        self.SynergiesStart = time.time()
        
        self.plot_options = dict(width=800, height=200, tools=[self.hover, self.tools]) # Set plot width, height, and other plot options
        self.bar_options = dict(width=400, height=200, tools=[self.hover, self.tools]) # Set plot width, height, and other plot options
        self.updateValue = True # Internal state for updating of plots
        self.MuscleSource, self.SynergySource, self.LinePlots, self.BarPlots, self.MusclesBarData, self.synergiesBarData = self.definePlot() # Define various plots. Return handles for data source (self.source) and combined plot (self.pAll)
        self.doc = curdoc() # Save curdoc() to make sure all threads see the same document. curdoc() refers to the Bokeh web document
        self.layout() # Set the checkboxes and overall layout of the webpage 
        self.prev_y1 = 0
         

    def definePlot(self):
        # Define MusclesPlot 

        MusclesPlot = figure(**self.plot_options, title="Activaciones Musculares")
        MusclesPlot.xaxis.axis_label = "Tiempo (s)"
        MusclesPlot.yaxis.axis_label = "Activación (%)"
        MusclesPlot.y_range = Range1d(start=0.0, end=self.yAxisMax)

        MusclesBarPlot = figure(**self.bar_options, title="Activaciones Musculares")
        x = [i for i in range(1, self.MusclesNumber+1)]
        top = [i for i in range(1, self.MusclesNumber+1)]
        width = 0.5
        MusclesBarPlot.y_range = Range1d(start=0.0, end=self.yAxisMax)
        MusclesBar = MusclesBarPlot.vbar(x,top = top,width = width)
        MusclesBarData = MusclesBar.data_source.data
       
        # Define SynergiesPlot
        SynergiesPlot = figure(**self.plot_options, x_range=MusclesPlot.x_range, title="Computed Value") # Link x-axis of first and second graph
        SynergiesPlot.xaxis.axis_label = "Tiempo (s)"
        SynergiesPlot.yaxis.axis_label = "Activación (%)"
        SynergiesPlot.y_range = Range1d(start=0.0, end=self.yAxisMax)

        SynergiesBarPlot = figure(**self.bar_options, title="Activaciones Musculares")
        x = [i for i in range(1, self.SynergiesNumber+1)]
        top = [i for i in range(1, self.SynergiesNumber+1)]
        width = 0.5
        SynergiesBarPlot.y_range = Range1d(start=0.0, end=self.yAxisMax)
        SynergiesBar = SynergiesBarPlot.vbar(x,top = top,width = width)    
        SynergiesBarData = SynergiesBar.data_source.data

        # SynergiesPlot.extra_y_ranges = {"class": Range1d(start=-1, end=2)} # Add a secondary y-axis
        # SynergiesPlot.add_layout(LinearAxis(y_range_name="class", axis_label="Classification"), 'right') # Name and place the secondary y-axis on the right vertical edge of the graph
        
        # Define source data for all plots
        muscleData = {'x': [0]}
        for i in range(0, self.MusclesNumber):
            muscleData[f'y{i}'] = [0]
        MuscleSource = ColumnDataSource(data=muscleData)
        
        synergyData = {'x': [0]}
        for i in range(0, self.SynergiesNumber):
            synergyData[f'y{i}'] = [0]
        SynergySource = ColumnDataSource(data=synergyData)
        
        # Muscles Plot Lines
        MuscleLines = []
        items = []
        for i in range(self.MusclesNumber):
            MuscleLines.append(MusclesPlot.line(x='x', y=f'y{i}', source=MuscleSource, color=self.colors[i], line_width=1))
            items.append([params.SensorStickers[i], [MuscleLines[i]]])
        legend = Legend(items=items, location=(10, 30))
        MusclesPlot.add_layout(legend, 'right')
        MusclesPlot.legend.click_policy = "hide" # Plot line may be hidden by clicking the legend marker 
        
        #Synergies Plot Lines
        SynergiesLines = []
        items = []
        for i in range(self.SynergiesNumber):
            SynergiesLines.append(SynergiesPlot.line(x='x', y=f'y{i}', source=SynergySource, color=self.colors[i], line_width=1))
            items.append([f"Synergy {i+1}", [SynergiesLines[i]]])
        legend = Legend(items=items, location=(10, 30))

        SynergiesPlot.add_layout(legend, 'right')
        SynergiesPlot.legend.click_policy = "hide"  # Plot line may be hidden by clicking the legend marker
        
        # Combine all plots into a gridplot for better vertical alignment
        LinePlots = gridplot([[MusclesPlot],[SynergiesPlot]], height=270, width=800, toolbar_location="below")
        BarPlots = gridplot([[MusclesBarPlot],[SynergiesBarPlot]], height=270, width=400, toolbar_location="below")

        return MuscleSource, SynergySource, LinePlots, BarPlots, MusclesBarData, SynergiesBarData # Return handles to data source and gridplot

    @gen.coroutine
    def update(self, MusclesActivations, SynergiesActivations):
        if self.updateValue: # Update the plots only if the 'self.updateValue' is True
            
            # Update the Muscles plot
            MusclesLastX = self.MuscleSource.data['x'][-1]  # Increment the time step on the x-axis of the graphs
            

            
            MuscleActivationsSize = len(MusclesActivations)
            MusclesDictionary = {}
            
            if MusclesActivations == []:
                   MusclesDictionary['x'] = []
            elif np.asarray(MusclesActivations).shape[0] == 1:
                MusclesDictionary['x'] = [MusclesLastX + time.time() - self.MusclesStart]
                self.MusclesStart = time.time()
            else:
                x = np.linspace(MusclesLastX, MusclesLastX + time.time() - self.MusclesStart, MuscleActivationsSize, endpoint=False)
                MusclesDictionary['x'] = x + (x[1]-x[0]) 
                self.MusclesStart = time.time()
            
            # try:
            #     print(x, time.time() - self.start)
            # except:
            #     self.start = time.time()
            # self.start = time.time()
            #  MusclesDictionary = {'x': np.linspace(Musclesx, Musclesx + MuscleActivationsSize*self.timeStep, MuscleActivationsSize)}
            
            for i in range(self.MusclesNumber):
                if MusclesActivations == []:
                    MusclesDictionary[f'y{i}'] = []
                elif np.asarray(MusclesActivations).shape[0] == 1:
                    MusclesDictionary[f'y{i}'] = [np.asarray(MusclesActivations)[0][i]]    
                else:
                    MusclesDictionary[f'y{i}'] = np.asarray(MusclesActivations)[:,i]
    
            self.MuscleSource.stream(MusclesDictionary, rollover=self.points2Display) # Feed new data to the graphs and set the rollover period to be xx samples

            if MusclesActivations == []:
                pass
            elif np.asarray(MusclesActivations).shape[0] == 1:
                self.MusclesBarData['top'] = np.asarray(MusclesActivations)[0] #[i for i in self.SynergiesNumber]
            else:
                self.MusclesBarData['top'] = np.asarray(MusclesActivations)[-1]

            # Update the Synergies plot
            SynergiesLastX = self.SynergySource.data['x'][-1] 
            SynergiesActivationsSize = len(SynergiesActivations)
            
            SynergiesDictionary = {}
            if SynergiesActivations == []:
                SynergiesDictionary['x'] = []
            elif np.asarray(SynergiesActivations).shape[0] == 1:
                SynergiesDictionary['x'] = [SynergiesLastX + time.time() - self.SynergiesStart]
                self.SynergiesStart = time.time()
            else:
                x = np.linspace(SynergiesLastX, SynergiesLastX + time.time() - self.SynergiesStart, SynergiesActivationsSize, endpoint=False)
                SynergiesDictionary['x'] = x + (x[1]-x[0]) 
                self.SynergiesStart = time.time()
            
            for i in range(0, self.SynergiesNumber):
                if SynergiesActivations == []:
                    SynergiesDictionary[f'y{i}'] = []
                elif np.asarray(SynergiesActivations).shape[0] == 1:
                    SynergiesDictionary[f'y{i}'] = [np.asarray(SynergiesActivations)[0][i]]
                else:
                    SynergiesDictionary[f'y{i}'] = np.asarray(SynergiesActivations)[:,i]

            self.SynergySource.stream(SynergiesDictionary, rollover=self.points2Display) # Feed new data to the graphs and set the rollover period to be xx samples

            # Update the synergies Bar plot
            if SynergiesActivations == []:
                pass
            elif np.asarray(SynergiesActivations).shape[0] == 1:
                self.synergiesBarData['top'] = np.asarray(SynergiesActivations)[0] #[i for i in self.SynergiesNumber]
            else:
                self.synergiesBarData['top'] = np.asarray(SynergiesActivations)[-1]


    def checkbox1Handler(self, attr, old, new):
        if 0 in list(new):  # Verify if the first checkbox is ticked currently
            if 0 not in list(old): # Perform actions if the first checkbox was not ticked previously, i.e., it changed state recently 
                self.running.set() # Set the Flag
                self.callbackFunc(self, self.running) # Restart the Sensor thread
        else:
            self.running.clear()  # Kill the Sensor thread by clearing the Flag
        if 1 in list(new):  # Verify if the second checkbox is ticked
            self.updateValue = True # Set internal value to continue updating the graphs
        else:
            self.updateValue = False # Set internal value to stop updating the graphs

    def CheckboxCallback(self,attr, old, new):
        print("CheckboxCallback")

    def layout(self):
        # Build interactive user interface
        checkbox1 = CheckboxGroup(labels=["Start/Stop Sensor Thread", "Start/Stop Plotting"], active=[0, 1]) # Create checkboxes
        checkbox1.on_change('active', self.checkbox1Handler) # Specify the action to be performed upon change in checkboxes' values 
        # Build presentation layout
        layout = column(self.text1,self.EmptyContainerTitle, row(self.EmptyContainerLeft, self.LinePlots,self.BarPlots)) # Place the text at the top, followed by checkboxes and graphs in a row below 
        self.doc.title = "Real Time Sensor Data Streaming" # Name of internet browser tab
        self.doc.add_root(layout) # Add the layout to the web document