# server.py 
import socket                                         
import time

# create a socket object
serversocket = socket.socket(
	        socket.AF_INET, socket.SOCK_STREAM) 

# get local machine name
host = socket.gethostname()                           

port = 9999                                           

# bind to the port
serversocket.bind((host, port))                                  

# queue up to 5 requests
serversocket.listen(5)                                           

print ("Running Server on ", host," Port: ",  port)
# establish a connection
clientSocket,addr = serversocket.accept()      

print("Got a connection from %s" % str(addr))

deviceName = clientSocket.recv(1024)
print ("Device Connected : ", deviceName.decode('ascii'), "\nSending Image")

imgData = "THIS WOULD ACTUALLY BE THE IMAGE DATA OF 640x480."
clientSocket.send(imgData.encode('ascii'))

deviceResult = clientSocket.recv(1024)
print ("Got the device result as ",deviceResult.decode('ascii'))
clientSocket.close()
