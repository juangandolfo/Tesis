'''import streamlit as st
import pandas as pd
import numpy as np
import time
import altair as alt

# CLASSES --------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------
class Buffer:
    def __init__(self, MusclesNumber, Pts2Display):
        self.Buffer = np.zeros((Pts2Display, MusclesNumber))
        self.timestamps = np.zeros(Pts2Display)  # Initialize timestamps or indices
        self.timestep = 0
        self.Pts2Display = Pts2Display  # Store the number of points to display

    def add_point(self, data):
        self.Buffer = np.roll(self.Buffer, -1, axis=0)
        self.Buffer[-1] = data
        self.timestamps = np.roll(self.timestamps, -1)
        self.timestamps[-1] = self.timestep  # Update timestamp or index
        self.timestep += 1
        return self.Buffer, self.timestamps

    def add_matrix(self, data):
        for line in data:
            self.add_point(line)

    def get_recent_data(self, seconds=10):
        max_timestamp = self.timestamps[-1]
        min_timestamp = max_timestamp - seconds * 1000  # Convert seconds to milliseconds
        
        # Find indices within the time range
        indices = np.where((self.timestamps >= min_timestamp) & (self.timestamps <= max_timestamp))[0]
        
        # Get the corresponding data
        recent_data = self.Buffer[indices]
        recent_timestamps = self.timestamps[indices]
        
        return recent_data, recent_timestamps

# INSTANCES ------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------

# CREATE THE BUFFERS
Pts2Display = round(1000 * 10)  # 10 seconds worth of data (assuming 1000Hz sampling)
MusclesNumber = 1
MusclesBuffer = Buffer(MusclesNumber, Pts2Display)
SynergiesBuffer = Buffer(MusclesNumber, Pts2Display)

# Configurar la página de Streamlit
st.title('Visualización de Músculos y Sinergias en Tiempo Real')

# Create a Chart object without data initially
chart = st.altair_chart(alt.Chart(pd.DataFrame()).mark_line().encode(
    x='Timestamp:T',  # Timestamp field should be explicitly typed as time
    y=alt.Y('value:Q', title='Value'),  # Value field should be explicitly typed as quantitative
    color=alt.Color('variable:N', legend=None)  # Variable field should be explicitly typed as nominal
).properties(width=600))  # Adjust width as needed

# Function to update charts
def update_charts():
    global muscles_data
    
    new_data = np.random.rand(40, MusclesNumber)  
    MusclesBuffer.add_matrix(new_data)
    muscles_data, timestamps = MusclesBuffer.get_recent_data(seconds=10)
    
    # Convert deque to DataFrame with column names
    muscles_df = pd.DataFrame(muscles_data, columns=[f'Muscle {i+1}' for i in range(MusclesNumber)])
    muscles_df['Timestamp'] = timestamps
    
    # Melt the data to long format for Altair
    muscles_melted = muscles_df.melt(id_vars=['Timestamp'], var_name='variable', value_name='value')
    
    # Update Altair chart with new data
    chart.altair_chart(alt.Chart(muscles_melted).mark_line().encode(
        x='Timestamp:T',  # Timestamp field should be explicitly typed as time
        y=alt.Y('value:Q', title='Value'),  # Value field should be explicitly typed as quantitative
        color=alt.Color('variable:N', legend=None)  # Variable field should be explicitly typed as nominal
    ).properties(width=600))  # Adjust width as needed

# MAIN LOOP ------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------

if __name__ == '__main__':
    while True:
        time.sleep(1/60)  # Update approximately at 60Hz
        update_charts()
'''

import numpy as np

zeros = np.zeros((2,3))
y1 = zeros[:,0]
print(y1)