from bokeh.plotting import figure
from bokeh.models import LinearAxis, Range1d, HoverTool, ColumnDataSource, Legend
from bokeh.layouts import gridplot, column, row
from bokeh.models.widgets import CheckboxGroup, Div
from bokeh.io import curdoc
from tornado import gen

import numpy as np

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
        
        self.MusclesNumber = 8
        self.SynergiesNumber = 8
        self.colors = ["firebrick", "indigo", "green", "blue", "orange", "purple", "brown", "pink"]
        self.ChannelName = ["Channel 1", "Channel 2", "Channel 3", "Channel 4", "Channel 5", "Channel 6", "Channel 7", "Channel 8"]
        self.sampleRate = 2148
        self.timeStep = 1/self.sampleRate

        self.plot_options = dict(width=800, height=200, tools=[self.hover, self.tools]) # Set plot width, height, and other plot options
        self.bar_options = dict(width=400, height=200, tools=[self.hover, self.tools]) # Set plot width, height, and other plot options
        self.updateValue = True # Internal state for updating of plots
        self.MuscleSource, self.SynergySource, self.LinePlots, self.BarPlots = self.definePlot() # Define various plots. Return handles for data source (self.source) and combined plot (self.pAll)
        self.doc = curdoc() # Save curdoc() to make sure all threads see the same document. curdoc() refers to the Bokeh web document
        self.layout() # Set the checkboxes and overall layout of the webpage 
        self.prev_y1 = 0
         

    def definePlot(self):
        # Define MusclesPlot 
        MusclesPlot = figure(**self.plot_options, title="Activaciones Musculares")
        MusclesPlot.xaxis.axis_label = "Tiempo (s)"
        MusclesPlot.yaxis.axis_label = "Activación (%)"
        MusclesPlot.y_range = Range1d(start=0.0, end=1.0)

        MusclesBarPlot = figure(**self.bar_options, title="Activaciones Musculares")
        x = [1, 2, 3, 4, 5]
        top = [1, 2, 3, 4, 5]
        width = 0.5
        # plotting the graph
        MusclesBar = MusclesBarPlot.vbar(x,
                top = top,
                width = width)    
        MusclesBarData = MusclesBar.data_source.data
        MusclesBarData['top'] = [5, 4, 3, 1, 0]
       
        # Define SynergiesPlot
        SynergiesPlot = figure(**self.plot_options, x_range=MusclesPlot.x_range, title="Computed Value") # Link x-axis of first and second graph
        SynergiesPlot.xaxis.axis_label = "Tiempo (s)"
        SynergiesPlot.yaxis.axis_label = "Activación (%)"
        SynergiesPlot.y_range = Range1d(start=0.0, end=1.0)

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
        
        # Define graphs for each plot
        # Muscles Plot
        MuscleLines = []
        items = []
        for i in range(self.MusclesNumber):
            MuscleLines.append(MusclesPlot.line(x='x', y=f'y{i}', source=MuscleSource, color=self.colors[i], line_width=1))
            items.append([self.ChannelName[i], [MuscleLines[i]]])
        legend = Legend(items=items, location=(10, -5))
        MusclesPlot.add_layout(legend, 'right')
        MusclesPlot.legend.click_policy = "hide" # Plot line may be hidden by clicking the legend marker 
        
        #Synergies Plot
        SynergiesLines = []
        items = []
        for i in range(self.SynergiesNumber):
            SynergiesLines.append(SynergiesPlot.line(x='x', y=f'y{i}', source=SynergySource, color=self.colors[i], line_width=1))
            items.append([f"Synergy {i+1}", [SynergiesLines[i]]])
        legend = Legend(items=items, location=(10, -5))

        SynergiesPlot.add_layout(legend, 'right')
        SynergiesPlot.legend.click_policy = "hide"  # Plot line may be hidden by clicking the legend marker
        # Combine all plots into a gridplot for better vertical alignment
        LinePlots = gridplot([[MusclesPlot],[SynergiesPlot]], height=270, width=800, toolbar_location="below")
        BarPlots = gridplot([[MusclesBarPlot],[None]], height=270, width=400, toolbar_location="below")

        return MuscleSource, SynergySource, LinePlots, BarPlots # Return handles to data source and gridplot

    @gen.coroutine
    def update(self, MusclesActivations, SynergiesActivations):
        if self.updateValue: # Update the plots only if the 'self.updateValue' is True
            
            # Update the Muscles plot
            Musclesx = self.MuscleSource.data['x'][-1] + self.timeStep # Increment the time step on the x-axis of the graphs
            MuscleActivationsSize = len(MusclesActivations)
            
            MusclesDictionary = {'x': np.linspace(Musclesx, Musclesx + MuscleActivationsSize*self.timeStep, MuscleActivationsSize)}
            for i in range(self.MusclesNumber):
                MusclesDictionary[f'y{i}'] = MusclesActivations[:,i]+i*0.1
    
            self.MuscleSource.stream(MusclesDictionary, rollover=10000) # Feed new data to the graphs and set the rollover period to be xx samples

            # Update the Synergies plot
            Synergiesx = self.MuscleSource.data['x'][-1] + self.timeStep
            SynergiesActivationsSize = len(SynergiesActivations)
            
            SynergiesDictionary = {'x': np.linspace(Synergiesx, Synergiesx + SynergiesActivationsSize*self.timeStep, SynergiesActivationsSize)}
            for i in range(0, self.SynergiesNumber):
                SynergiesDictionary[f'y{i}'] = SynergiesActivations[:,i] * 0.1 + i*0.1

            self.SynergySource.stream(SynergiesDictionary, rollover=10000) # Feed new data to the graphs and set the rollover period to be xx samples


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