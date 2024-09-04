
# Herramienta interactiva para la visualización y el entrenamiento de Sienrgias Musculares 

## Resumen 
En este proyecto se desarrolló una interfaz hombre-computadora, en la que la actividad muscular del sujeto, obtenida a través de electromiografía de superficie, controla un cursor bidimensional en una pantalla, pero solo si dicha actividad incluye el reclutamiento de patrones específicos de coordinación muscular, llamados sinergias musculares. A través de la visualización del movimiento del cursor en la pantalla, la herramienta permite que el sujeto reciba retroalimentación en tiempo real sobre sus sinergias musculares, estableciendo un sistema de control de retroalimentación human-in-the-loop. 
 
## Módulos 
La herramienta consta de 4 módulos:
 - Servidor de datos
 - Módulo de procesamiento
 - Cursor
 - Visualización

#### Servidor de datos
El servidor de datos es el encargado de implementar la comunicación entre el sistema de adquisición de datos de EMG con el resto de la herramienta. También implementa un panel de control para gestionar la configuracion del sistema de adquisición y el control de la herramienta.
#### Módulo de procesamiento
Este módulo realiza los calculos asociados al procesamiento de los datos. Sus tareas mas importantes son la detección de los parametros de calibracion, incluidas las sinergias musculares. El filtrado y normalización de los datos adquiridos. Y la transformación de activaciones musculares a desplazamientos del cursor. 
#### Cursor
El objetivo de este módulo es implementar la interfaz visual del cursor. Su principal tarea es gestionar la posición del cursor y sus colisiones con los objetos y bordes.
#### Visualización
La visualización sirve como interfaz visual para observar el historico de los últimos segundos de las activaciones musculares logradas, asi como las activaciones de las sinergias musculares.

## Guia de instalación
Previo a utilizar la herramienta se deben instalar algunos paquetes y drivers. En el repositorio se encuentra el archivo con la lista de requerimientos bajo el nombre de requirements.txt.

Se puede instalar manualmente los paquetes o automaticamente mediante el comando:

    Python -m pip install -r requirements.txt

El driver a instalar es utilizado por la API de la estación de adquisición de datos de Delsys. El driver se llama USBXpress y existen versiones para varias arqiutecturas, x32, x64 y x84. En este proyecto se utiliza la de x64. Dentro de la carpeta SiliconLabs se encuentra el instalador del driver. Tambien se encuentra la DLL dentro de la siguiente carpeta:

    ./Resources

 bajo el nombre:
    
    SiUSBXp_64.dll

Una vez instalados los requerimientos y el driver, se ejecuta el archivo para comenzar a utilizar la herramienta

    Executable.py 






