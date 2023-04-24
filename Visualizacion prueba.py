import socket
import time
import threading
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import random

global bar_values, bar_values_history, bar_values_history, bar_values, bar_checkboxes

def generate_example_data():
    data = []
    for i in range(2000 * 10):
        value = random.randint(0, 100)
        data.append(value)
    return data

# Función para obtener los datos de la API y actualizar la gráfica de barras
def update_bar_chart():
    # Hacer una solicitud a la API TCP/IP para obtener los datos de las barras
    # Aquí debes agregar el código para conectarte al servidor API y enviar solicitudes.
    # Los datos recibidos de la API deben ser almacenados en una lista o en una variable global.
    # Generar datos de ejemplo
    example_data = generate_example_data()

    # Actualizar los valores de las barras con los nuevos datos
    
    bar_values = example_data[:8]
    bar_values_history.append(bar_values)


    # Actualizar la gráfica de barras con los nuevos valores
    ax.clear()
    ax.bar(range(len(bar_values)), bar_values)
    canvas.draw()

    # Programar la siguiente actualización de la gráfica después de 1 segundo
    root.after(1000, update_bar_chart)

# Función para obtener los datos de los últimos 10 segundos y actualizar la gráfica de puntos
def update_point_chart():
    # Obtener los datos de los últimos 10 segundos
    # Obtener los datos de ejemplo de los últimos 10 segundos
    example_data = generate_example_data()[-200:]

    # Actualizar la lista de valores históricos para todas las barras
    
    bar_values_history.append(example_data)

    history_data = bar_values_history[-10:]

    # Calcular los cambios de valores para cada barra
    diffs = []
    for i in range(1, len(history_data)):
        diff = history_data[i] - history_data[i-1]
        diffs.append(diff)

    # Actualizar la gráfica de puntos con los cambios de valores
    ax.clear()
    ax.plot(diffs, 'o-')
    ax.set_xlabel('Tiempo (segundos)')
    ax.set_ylabel('Cambio en valores')
    canvas.draw()

    # Programar la siguiente actualización de la gráfica después de 1 segundo
    root.after(1000, update_point_chart)

# Función para actualizar la selección de barras
def update_bars_selection():


    # Obtener la selección de barras del usuario
    selected_bars = []
    for i in range(len(bar_checkboxes)):
        if bar_checkboxes[i].get() == 1:
            selected_bars.append(i)

    # Actualizar la gráfica de barras con las barras seleccionadas
    selected_values = [bar_values[i] for i in selected_bars]
    ax.clear()
    ax.bar(range(len(selected_values)), selected_values)
    canvas.draw()

    # Actualizar la lista de valores históricos para las barras seleccionadas
    selected_history_values = [[bar_values_history[i][j] for i in selected_bars] for j in range(len(bar_values_history))]
    bar_values_history = selected_history_values

# Crear la ventana principal de la aplicación
root = tk.Tk()
root.title('Visualización de datos')

# Crear la gráfica de barras
fig = Figure(figsize=(6, 3), dpi=100)
ax = fig.add_subplot(111)
bar_values = [0] * 8
ax.bar(range(len(bar_values)), bar_values)
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().grid(row=0, column=0)

# Crear la gráfica de puntos para los cambios en los últimos 10 segundos
fig2 = Figure(figsize=(6, 3), dpi=100)
ax
