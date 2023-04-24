import matplotlib.pyplot as plt
import numpy as np
import random

# Creamos la figura y los ejes
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10,5))

# Creamos los datos iniciales
datos = [random.random() for _ in range(8)]

# Creamos una matriz para cada barra que almacene los últimos 5 segundos de datos
historial = [[] for _ in range(8)]

dataStack = [[] for _ in range(8)]

promedio = [[] for _ in range (8)]

# Definimos la función para actualizar los datos
def actualizar_datos():
    global datos, historial, dataStack, promedio
    
    # Agregamos nuevos datos aleatorios a cada barra
    nuevos_datos = [random.random() for _ in range(8)]
    for i in range(8):
        datos[i] = nuevos_datos[i]
        dataStack[i].append(nuevos_datos[i])
        if len(dataStack[i]) > 20:
            promedio[i] = np.mean(dataStack[i])
            dataStack[i] = []
            historial[i].append(promedio[i])   
        #historial[i].append(nuevos_datos[i])
        
        # Mantenemos el historial de los últimos 5 segundos
        if len(historial[i]) > 5:
            historial[i] = historial[i][-5:]
    
    # Actualizamos las gráficas de barras
    for i in range(8):
        barra = ax1.patches[i]
        barra.set_height(datos[i])
        barra.set_facecolor(colores[i])
    
    # Actualizamos la gráfica de puntos
    for i in range(8):
        puntos = historial[i]
        ax2.lines[i].set_ydata(puntos)
        ax2.lines[i].set_xdata(np.arange(len(puntos)))
        #ax2.lines[i].set_xdata(np.arange(0,len(puntos),0.1))
        ax2.lines[i].set_color(colores[i])
    
    # Redibujamos la figura
    fig.canvas.draw()

# Creamos las gráficas de barras y de puntos
colores = ['b', 'g', 'r', 'c', 'm', 'y', 'k', 'orange']
#colores = [np.random.rand(3,) for _ in range(8)]
ax1.bar(np.arange(8), datos, color=colores)
#ax1.bar(np.arange(8), datos, color='blue')
ax1.set_ylim([0, 1])
ax1.set_xlabel('Barra')
ax1.set_ylabel('Valor')
ax1.set_title('Gráfica de barras')

ax2.set_xlim([0, 5])
ax2.set_ylim([0, 1])
ax2.set_xlabel('Tiempo (segundos)')
ax2.set_ylabel('Valor')
ax2.set_title('Gráfica de puntos')

for i in range(8):
    puntos = historial[i]
    ax2.plot(np.arange(len(puntos)), puntos, color=colores[i])

# Actualizamos los datos cada 100 milisegundos
timer = fig.canvas.new_timer(interval=1)
timer.add_callback(actualizar_datos)
timer.start()

plt.show()
