import socket

# create a socket object
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 

# get local machine name
host = socket.gethostname()                           

port = 9999

# connection to hostname on the port.
serverSocket.connect((host, port))                               

deviceName = "ZEDBOARD"
serverSocket.send(deviceName.encode('ascii'))

#Receive the Image
image = serverSocket.recv(1024)
print ("Got the image as : ", image.decode('ascii'))

sampleDataString = "FD,2,label1,label2\nLO,1.21,3.44,0.99"
serverSocket.send(sampleDataString.encode('ascii'))

serverSocket.close()
