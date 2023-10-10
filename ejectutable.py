import API_Functions as API
import API_Server
from threading import Thread
import Processing_Module as PM
import time

start_thread = Thread(target=API.Start)
start_thread.start()
time.sleep(0.5)
API_server_thread=Thread(target=API_Server.API_Server)
API_server_thread.start()
time.sleep(0.5)
Processing_Module_Client_thread = Thread(target=PM.Processing_Module_Client)
Processing_Module_Server_thread = Thread(target=PM.Processing_Module_Server)
Processing_Module_Client_thread.start()
time.sleep(0.5)
Processing_Module_Server_thread.start()
time.sleep(0.5)
import Cursor 
Cursor_thread=Thread(target=Cursor.Cursor)
Cursor_thread.start()
