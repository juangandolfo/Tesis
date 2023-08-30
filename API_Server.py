import socket
import random
import json
from threading import Thread
import time
import API_Functions as API



HOST = "127.0.0.1"  # Standard adress (localhost)
PORT = 6001  # Port to listen on (non-privileged ports are > 1023)


# Start data streaming
start_thread = Thread(target=API.Start)
start_thread.start()

# Create a socket
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:

    # Link the socket to the IP and PORT selected: 
    s.bind((HOST, PORT))

    # Listen the inner connections:
    print("Server listening on", HOST, "port", PORT)
    s.listen()
    
    # Accept the connection and open a socket to receive and send data. 
    conn, addr = s.accept()
    with conn:
        print(f"Connected by {addr}")
        while True:
            data = conn.recv(1024)
            # Check if the received data is a GET request for "/data"
            if data.decode().strip() == "GET /data":
                response_data = API.PollData()
                response_json = json.dumps(response_data, separators=(',', ':')) # Convert the dictionary to JSON 
                response_json += "#DELIMITER#" # Add a delimiter at the final 
                conn.sendall(response_json.encode())
                print("Data sent:", response_json)
            else:
                # If the received data is not "GET /data", close the connection
                print("Invalid request")
                





