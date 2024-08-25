import numpy as np
from scipy.signal import butter, freqz
import matplotlib.pyplot as plt

# Parámetros del filtro
LPF_cutoff = 40       # Frecuencia de corte en Hz
LPF_order = 4         # Orden del filtro
sampleRate = 1000     # Frecuencia de muestreo en Hz

# Calcular la frecuencia de Nyquist y la frecuencia de corte normalizada
nyquist = 0.5 * sampleRate
normal_cutoff = LPF_cutoff / nyquist

# Crear el filtro pasa-bajos usando butter
coefficient2, coefficient1 = butter(LPF_order, normal_cutoff, btype='low', analog=False)

# Obtener la respuesta en frecuencia del filtro
w, h = freqz(coefficient2, coefficient1, worN=8000)

# Crear el gráfico de Bode
plt.figure(figsize=(10, 6))

# Magnitud en dB
plt.subplot(2, 1, 1)
plt.plot(w * nyquist / np.pi, 20 * np.log10(abs(h)), 'b')
plt.title('Diagrama de Bode del Filtro Pasa-Bajos')
plt.xlabel('Frecuencia (Hz)')
plt.ylabel('Magnitud (dB)')
plt.grid()

# Fase en grados
plt.subplot(2, 1, 2)
plt.plot(w * nyquist / np.pi, np.angle(h, deg=True), 'b')
plt.xlabel('Frecuencia (Hz)')
plt.ylabel('Fase (grados)')
plt.grid()

# Mostrar el gráfico
plt.show()
