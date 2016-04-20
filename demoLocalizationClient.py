import socket
import time

# create a socket object
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 

# get local machine name
host = socket.gethostname()                           

port = 7892

# connection to hostname on the port.
serverSocket.connect((host, port))                               

requestName = "Localization"

while True:
	serverSocket.send(requestName.encode('ascii'))
	print ("Sent Data Identifier : ",requestName)
	if requestName == "FaceDetectionTransmit":
		##Code to receive Image
		with open('received_file.jpg', 'wb') as f:
		    print ('file opened')
		    while True:
		        #print('receiving data...')
		        data = serverSocket.recv(1024)
		        #print('DATA BEING RECEIVED:\t', (data))
		        if not data:
		            break
		        # write data to a file
		        f.write(data)
		f.close()
		print ("File Received")
		serverSocket.close()
		print ("Reconnecting to Host : ",host," Port : ",port)
		serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
		# get local machine name
		host = socket.gethostname()                           
		port = 7891
		serverSocket.settimeout(3)
		serverSocket.connect((host, port))
	elif requestName == "FaceDetectionReceive":
		handshake = serverSocket.recv(1024)
		handshake = handshake.decode('ascii')
		if handshake == "Send FD Data":
			fdResult = "FD,2,Label1,Label2"
			serverSocket.send(fdResult.encode('ascii'))
			serverSocket.recv(1024)
	elif requestName == "Localization":
		handshake = serverSocket.recv(1024)
		handshake = handshake.decode('ascii')
		if handshake == "Send LO Data":
			loResult = "LO,1.2314,2.5426,0.1243"
			serverSocket.send(loResult.encode('ascii'))
			serverSocket.recv(1024)
	else:
		print ("Please specify request name correctly")
		serverSocket.close()
