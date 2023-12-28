from GlobalParameters import *
from Aero_Nuevo import *
import API_Server_Nuevo as API_Server
import Processing_Module_Nuevo as PM
import time
from threading import Thread
import Delsys_API_Server


aero_instance.Start()
time.sleep(0.1)
if ModoDelsys:
    API_server_thread=Thread(target=Delsys_API_Server.API_Server)  
    API_server_thread.start()
else:
    API_server_thread=Thread(target=API_Server.API_Server)  
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

