from biosppy.signals import emg
import numpy as np
import csv
import matplotlib.pyplot as plt
from scipy.signal import butter
from scipy import signal

# Variables para almacenar los datos
t = []  # Tiempo
m1_signal = []  # Señal M1
m2_signal = []  # Señal M2

# Abre el archivo CSV en modo lectura
with open('Prueba1.csv', 'r') as archivo_csv:
    lector_csv = csv.reader(archivo_csv, delimiter=';')  # Especifica el delimitador como punto y coma
    
    # Ignora la primera fila (encabezados)
    next(lector_csv)
    
    # Lee las filas y almacena los datos en las listas correspondientes
    for fila in lector_csv:
        #t.append(float(fila[0]))  # Columna 'X[s]' como tiempo
        m1_signal.append(float(fila[1]))  # Columna 'M1' como señal M1
        m2_signal.append(float(fila[2]))  # Columna 'M2' como señal M2
        t.append(float(fila[0]))  # Columna 'M1' como señal M1

#Frecuencia
fourier_transform = np.fft.fft(m1_signal)
frequencies = np.fft.fftfreq(len(m1_signal), 0.001)

#Graficar las señales M1 y M2
plt.scatter(t, m1_signal, label='EMG', color='purple', marker='o', s=3)
plt.scatter(t, m2_signal, label='EMG', color='orange', marker='o', s=3)
plt.xlabel('Tiempo (s)')
plt.ylabel('Amplitud')
plt.title('Señal EMG')
plt.legend()
plt.grid(True)
plt.show()

# Graficar la Transformada de Fourier
plt.subplot(2, 1, 2)
plt.plot(frequencies, np.abs(fourier_transform))
plt.xlabel('Frecuencia (Hz)')
plt.ylabel('Amplitud')
plt.title('Transformada de Fourier')
plt.tight_layout()  # Ajustar el diseño de los subgráficos
plt.show()
