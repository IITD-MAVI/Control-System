#!python3
import socket
import time
import threading
import subprocess
import re

#Class Definitions for different components
class SignBoardDetect:
	def __init__(self,value):
		self.value = value

class TextureDetect:
	def __init__(self,texture,potHole):
		self.texture = texture
		self.pothole = pothole

class FaceDetection:
	def __init__(self,noOfFaces,nameArray):
		self.noOfFaces = noOfFaces
		self.nameArray = nameArray

class PositionInfo:
	def __init__(self,pos_x,pos_y,pos_z):
		self.pos_x = pos_x
		self.pos_y = pos_y
		self.pos_z = pos_z

#lock for printing status of threads
lock = threading.Lock()

## Threads to be used for 	1. SignBoard Processing
##				2. Camera Input Capture
##				3. Communication Handling for the ZedBoard
##				4. Communication Handling for the Mobile App
##				5. Texture Output


##Function for Capturing SignBoard Processing Output
#TODO: Replace with Actual SignBoard Program
def signBoardProcess():
	while True:
		time.sleep(1)	#To be reviewed by Dedeepya
		with lock:	#So that image is not being read/written
			signBoardProgram = subprocess.Popen(["./demoSignBoard.sh","currentColorFrame.jpeg"],stdout=subprocess.PIPE, shell = True)
			(signBoardValue,err) = signBoardProgram.communicate()
		signBoardValue = signBoardValue.decode("utf-8")
		if signBoardValue == "True":
			print ("SignBoard Detected")
		else:
			print ("No SignBoard")

##Function for Capturing Texture output
#TODO: 	Replace with Actual Texture Detection Program
#	Create variable for actual terrain name, etc
def textureDetectProcess():
	while True:
		time.sleep(1)
		with lock:
			textureDetectProgram = subprocess.Popen(["./demoTextureDetect.sh","currentColorFrame.jpeg","currentDepthFrame.mat"],stdout=subprocess.PIPE, shell = True)
			(textureOutput,err) = textureDetectProgram.communicate()
		textureDetectResult = re.findall("[^,]+",textureOutput.decode("utf-8"))
		terrainValue = [[0 for x in range(3)] for x in range(3)]
		for i in range(3):
			for j in range(3):
				terrainValue[i][j] = textureDetectResult[3*i + j + 1]
		potHoleVar = textureDetectResult[10]
		#print ("Texture String : ",textureDetectResult[0])
		print ("terrainValue : ", terrainValue)
		print ("potHoleVar : ", potHoleVar)


##Function for Capturing the FaceDetection/GPS Data from ZedBoard
def zedBoardTransaction():
	while True:
		time.sleep(2)
		dataIdentifier = zedBoardClientSocket.recv(1024)
		dataIdentifier = dataIdentifier.decode('ascii')
		if dataIdentifier == "FaceDetectionTransmit":	#Munib to have code for receiving jpeg
			#Code for Sending JPEG
			print ("Identified as FaceDetection Image Request. Sending Image")
			with lock:
				jpegImage = "currentGrayscaleFrame.jpeg"
				f = open(jpegImage,'rb')
				l = f.read(1024)
				while (l):
					zedBoardClientSocket.send(l)
					l = f.read(1024)
				f.close()
			print ("Image Sent")
		elif dataIdentifier == "FaceDetectionReceive":	#Munib
			##Code for Receiving Face Detection Results

			print ("Identified as FaceDetection Results")
			#Handshake for sending FD Data
			stringForFDDataRequest = "Send FD Data"
			zedBoardClientSocket.send(stringForFDDataRequest.encode('ascii'))

			faceDetectionResult = zedBoardClientSocket.recv(1024)
			faceDetectionResult = faceDetectionResult.decode('ascii')
			fdResultArray = re.findall("[^,]+",faceDetectionResult)
			noOfFaces = fdResultArray[1]
			if noOfFaces == "0":
				print ("No Faces in the frame")
			else:
				for iterator in range(int(noOfFaces)):
					print ("Face",iterator," Label: ",fdResultArray[2+iterator])
		elif dataIdentifier == "Localization":	#Munib
			#Code for Handling Localization Data
			print ("Identified as location data")
			#Handshake for sending Localization Data
			stringForLODataRequest = "Send LO Data"
			zedBoardClientSocket.send(stringForLODataRequest.encode('ascii'))

			localizationResult = zedBoardClientSocket.recv(1024)
			localizationResult = localizationResult.decode('ascii')
			loResultArray = re.findall("[^,]+",localizationResult)
			(pos_x,pos_y,pos_z) = float(loResultArray[1]),float(loResultArray[2]),float(loResultArray[3])
			print ("Localization Data :: X:",pos_x," Y:",pos_y," Z:",pos_z)
		else:
			print ("Unidentified Data Identifier: ", dataIdentifier)
	
def createServerForZedBoard():
	# create a socket object
	serversocketForZB = socket.socket(
		        socket.AF_INET, socket.SOCK_STREAM) 
	
	# get local machine name
	host = socket.gethostname()                           
	
	port = 9999                                           
	
	# bind to the port
	serversocketForZB.bind((host, port))                                  
	
	# queue up to 5 requests
	serversocketForZB.listen(5)                                           
	
	print ("Server running on ", host," Port: ",  port, "for ZedBoard")
	
	zedBoardClientSocket,zedBoardClientAddr = serversocketForZB.accept()
	print ("Got a connection from ",zedBoardClientAddr)

def createServerForMobileApp():
	# create a socket object
	serversocketForMA = socket.socket(
		        socket.AF_INET, socket.SOCK_STREAM) 
	
	# get local machine name
	host = socket.gethostname()                           
	
	port = 1010 
	
	# bind to the port
	serversocketForMA.bind((host, port))                                  
	
	# queue up to 5 requests
	serversocketForMA.listen(5)                                           
	
	print ("Server running on ", host," Port: ",  port, "for mobile app")
	mobileClientSocket,mobileClientAddr = serversocketForMA.accept()

	print ("Got a connection from ",mobileClientAddr)


## Main Execution Flow Starts here
#createServerForZedBoard()
#createServerForMobileApp()

signBoardProcessThread = threading.Thread(target=signBoardProcess)
textureDetectProcessThread = threading.Thread(target=textureDetectProcess)
zedBoardTransactionThread = threading.Thread(target=zedBoardTransaction)
signBoardProcessThread.daemon = True
textureDetectProcessThread.daemon = True
zedBoardTransactionThread.daemon = True

signBoardProcessThread.start()
textureDetectProcessThread.start()
#zedBoardTransactionThread.start()
time.sleep(5)
