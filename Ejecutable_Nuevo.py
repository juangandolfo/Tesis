from Aero import AeroPy
import API_Server_Nuevo
import Processing_Module_Nuevo as PM
import time
from threading import Thread


aero_instance = AeroPy()
aero_instance.Start()
time.sleep(0.1)
API_server_thread=Thread(target=API_Server_Nuevo.API_Server)  
API_server_thread.start()
time.sleep(0.1)
Processing_Module_Client_thread = Thread(target=PM.Processing_Module_Client)
Processing_Module_Server_thread = Thread(target=PM.Processing_Module_Server)
Processing_Module_Client_thread.start()
time.sleep(0.1)
Processing_Module_Server_thread.start()
time.sleep(0.1)
import Cursor_Nuevo 
Cursor_thread=Thread(target=Cursor_Nuevo.Cursor)
Cursor_thread.start()

#import PruebaVisConBuffCopy 
#Visualizacion_thread = Thread(target=PruebaVisConBuffCopy.Visualization())
#Visualizacion_thread.start()

