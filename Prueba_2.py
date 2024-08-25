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
'''
import numpy as np

zeros = np.zeros((2,3))
y1 = zeros[:,0]
print(y1)'''

import pandas as pd
import matplotlib.pyplot as plt

# Cargar los datos desde un archivo CSV
file_path = r'Experiments\Experiment-20240808-265015.csv'  # Reemplaza con la ruta a tu archivo CSV
df = pd.read_csv(file_path)

# Define la columna de puntos y el valor constante
column_name = 'Muscle 1'  # Reemplaza con el nombre de la columna de tus puntos
constant_value = 1.6328374151216907  # Reemplaza con el valor constante que desees

# Define el rango de muestras a tomar (por ejemplo, de la fila 10 a la 20)
start_index = 40000  # Índice de la fila inicial (ajusta según tus necesidades)
end_index = 80000  # Índice de la fila final (ajusta según tus necesidades)

# Selecciona el rango de muestras de la columna
selected_data = df[column_name].iloc[start_index:end_index]

# Crear el gráfico
plt.figure(figsize=(10, 6))

# Graficar los puntos del rango seleccionado
plt.plot(-1*selected_data, marker='o', linestyle='None', label='Points')

# Superponer la línea del valor constante
plt.axhline(y=constant_value, color='red', linestyle='--', label=f'Peak = {constant_value}')
#plt.ylim(0.04, 0.07)  #

# Etiquetas y título
plt.xlabel('Sample number')
plt.ylabel('Muscle activation (mV)')
plt.title('Detected peak')
plt.legend()
plt.grid(True)

# Mostrar el gráfico
plt.show()

