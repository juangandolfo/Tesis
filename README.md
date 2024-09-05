# Herramienta interactiva para la visualización y el entrenamiento de Sinergias Musculares 

## Resumen 
En este proyecto se desarrolló una interfaz hombre-computadora, en la que la actividad muscular del sujeto, obtenida mediante electromiografía de superficie utilizando una estación Delsys, controla un cursor bidimensional en una pantalla, pero solo si dicha actividad incluye el reclutamiento de patrones específicos de coordinación muscular, llamados sinergias musculares. A través de la visualización del movimiento del cursor en la pantalla, la herramienta permite que el sujeto reciba retroalimentación en tiempo real sobre sus sinergias musculares, estableciendo un sistema de control de retroalimentación human-in-the-loop. 

## Guia de instalación
El proyecto se desarrolló utilizando Python 3.8. Previo a utilizar la herramienta se deben instalar algunos paquetes y drivers y configurar la licecia de la estación de adquisición de datos. 

#### Paquetes
En el repositorio se encuentra el archivo con la lista de requerimientos bajo el nombre

    .\requirements.txt

Se puede instalar manualmente los paquetes o automáticamente mediante el comando

    python -m pip install -r requirements.txt

#### Driver
El driver a instalar es utilizado por la API de la estación de adquisición de datos de Delsys. El driver se llama USBXpress y existen versiones para varias arqiutecturas, x32, x64 y x84. En este proyecto se utiliza la de x64. Dentro de la carpeta 

    .\SiliconLabs\MCU\USBXpress_SDK\Driver
    
Se encuentra el instalador del driver. Tambien se encuentra la DLL del driver en la ruta

    .\Resources\SiUSBXp_64.dll

#### Licencia
En este proyecto se utilizó una estación de Delsys Research+ como la estación de adquisición de datos. Para poder utilizar la API de la estación es necesario contar con una licencia provista por el fabricante. Para introducir la licencia se debe modificar el archivo

    .\AeroPy\TrignoBase.py

Dentro del archivo se deben popular las variables "Key" y "License" con la información de la licencia.

#### Uso de la herramienta

Una vez que la herramienta esté configurada e instalada, puedes iniciarla ejecutando el archivo 

    .\Executable.py. 

Asegúrate de tener la estación de adquisición de datos conectada y configurada correctamente. Al iniciar, se presentará un panel de control para gestionar la configuración del sistema y comenzar con el entrenamiento. 

#### Recomendaciones
Este proyecto utiliza muchos recursos por lo que se recomienda cerrar otras aplicaciones que consuman muchos recursos para asegurar un funcionamiento óptimo de la herramienta.
 
## Módulos 
La herramienta consta de 4 módulos:
 - Servidor de datos
 - Módulo de procesamiento
 - Cursor
 - Visualización

#### Servidor de datos
El servidor de datos es el encargado de implementar la comunicación entre el sistema de adquisición de datos de EMG con el resto de la herramienta. También implementa un panel de control para gestionar la configuracion del sistema de adquisición y el control de la herramienta.
#### Módulo de procesamiento
Este módulo realiza los calculos asociados al procesamiento de los datos. Sus tareas mas importantes son la detección de los parametros de calibración, incluidas las sinergias musculares. El filtrado y normalización de los datos adquiridos. Y la transformación de activaciones musculares a desplazamientos del cursor. 
#### Cursor
El objetivo de este módulo es implementar la interfaz visual del cursor. Su principal tarea es gestionar la posición del cursor y sus colisiones con los objetos y bordes.
#### Visualización
La visualización sirve como interfaz visual para observar el historico de los últimos segundos de las activaciones musculares logradas, asi como las activaciones de las sinergias musculares.











