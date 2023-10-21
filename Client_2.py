import socket
import json
import time
# TCP/IP visualization client ------------------------------------------------------------------------------
HOST = "127.0.0.1"  # The server's hostname or IP address
PORT_Client = 6002  # The port used by the API server

# Create a socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT_Client))

#-----------------------------------------------------------------------------------------------------------

# Function to send the request and receive the data from MP
def Get_data():
        request = "GET /data2"
        client_socket.sendall(request.encode())
        data = client_socket.recv(1024)
        response_data = json.loads(data.decode()) # Decode the received data
        
        return response_data
# ----------------------------------------------------------------------------------------------------------

while 1:
        print("dato cliente2:",Get_data())
        time.sleep(1)