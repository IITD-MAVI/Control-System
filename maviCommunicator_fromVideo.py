#!python3
import socket
import time
import threading
import subprocess
import re
import json
import cv2

#Class Definitions for different components
class SignBoardDetect:
	def __init__(self,isSignBoardDetected):
		self.isSignBoardDetected = isSignBoardDetected

class TextureDetect:
	def __init__(self,texture,pothole):
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

class ConsolidatedString:
	def __init__(self,signBoardString,textureString,faceDetectionString,positionString):
		self.signBoardString = signBoardString
		self.textureString = textureString
		self.faceDetectionString = faceDetectionString
		self.positionString = positionString

#lock for printing status of threads
#lock handles 3 scenarios: 1. Image exclusivity	2. Variable Updation  3. Status Printing
lock = threading.Lock()

## Threads to be used for 	1. SignBoard Processing
##				2. Camera Input Capture
##				3. Communication Handling for the ZedBoard
##				4. Communication Handling for the Mobile App
##				5. Texture Output


##Function for Capturing SignBoard Processing Output
#TODO: Replace with Actual SignBoard Program
def signBoardProcess():
	global signBoardValue
	while True:
		time.sleep(1)	#To be reviewed by Dedeepya
		with lock:	#So that image is not being read/written
			signBoardProgram = subprocess.Popen(["./signBoardDetect currentColorFrame.jpg"],stdout=subprocess.PIPE, shell = True)
			(signBoardValue,err) = signBoardProgram.communicate()
			signBoardValue = signBoardValue.decode("utf-8").strip()
		#if signBoardValue == "True":
		#	print ("SignBoard Detected")
		#else:
		#	print ("No SignBoard")

##Function for Capturing Texture output
#TODO: 	Replace with Actual Texture Detection Program
#	Create variable for actual terrain name, etc
def textureDetectProcess():
	global potHoleVar
	while True:
		time.sleep(1)
		with lock:
			textureDetectProgram = subprocess.Popen(["./demoTextureDetect.sh currentColorFrame.jpg"],stdout=subprocess.PIPE, shell = True)
			(textureOutput,err) = textureDetectProgram.communicate()
			textureDetectResult = re.findall("[^,]+",textureOutput.decode("utf-8"))
			for i in range(3):
				for j in range(3):
					terrainValue[i][j] = textureDetectResult[3*i + j + 1]
			potHoleVar = textureDetectResult[10]
		#print ("Texture String : ",textureDetectResult[0])
		#print ("terrainValue : ", terrainValue)
		#print ("potHoleVar : ", potHoleVar)


def imageCaptureFromVideo():
	vidcap = cv2.VideoCapture('HDVIDEO_1.mp4')
	startTime = time.perf_counter()
	while True:
		time.sleep(1)
		timeStamp = time.perf_counter() - startTime
		vidcap.set(0,timeStamp*1000)      # just cue to 20 sec. position
		success,image = vidcap.read()
		if success:
		    resized_image = cv2.resize(image,(640,480),0,0,cv2.INTER_CUBIC)
		    gray_image = cv2.cvtColor(resized_image, cv2.COLOR_BGR2GRAY)
		    with lock:
		    	cv2.imwrite("currentColorFrame.jpg", resized_image)     # save frame as JPEG file
		    	cv2.imwrite("currentGrayscaleFrame.jpg", gray_image)
		    print ("Last TimeStamp Captured : ",timeStamp)
		else:
			break

##Function for Capturing the FaceDetection/GPS Data from ZedBoard
def zedBoardTransaction():
	global noOfFaces
	global nameArray,labelArray
	global pos_x,pos_y,pos_z
	global zedBoardClientSocket
	while True:
		#print ("Waiting to receive Data Identifier")
		dataIdentifier = zedBoardClientSocket.recv(1024)
		dataIdentifier = dataIdentifier.decode('ascii')
		time.sleep(1)
		#print ("Data Identifier : ",dataIdentifier)
		if dataIdentifier == "FaceDetectionTransmit":	#Munib to have code for receiving jpeg
			#Code for Sending JPEG
			print ("Identified as FaceDetection Image Request. Sending Image")
			with lock:
				jpegImage = "currentGrayscaleFrame.jpg"
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
			receivedAcknowledge = "Received"
			zedBoardClientSocket.send(receivedAcknowledge.encode('ascii'))
			fdResultArray = re.findall("[^,]+",faceDetectionResult)
			with lock:
				noOfFaces = fdResultArray[1]
			if noOfFaces == "0":
				print ("No Faces in the frame")
				with lock:
					labelArray = []
					nameArray = []
			else:
				for iterator in range(int(noOfFaces)):
					print ("Face",iterator," Label: ",fdResultArray[2+iterator])
				with lock:
					labelArray = fdResultArray[2:]
					nameArray = []
					for label in labelArray:
						nameArray.append(LabelToName[label])
		elif dataIdentifier == "Localization":	#Munib
			#Code for Handling Localization Data
			print ("Identified as location data")
			#Handshake for sending Localization Data
			stringForLODataRequest = "Send LO Data"
			zedBoardClientSocket.send(stringForLODataRequest.encode('ascii'))

			localizationResult = zedBoardClientSocket.recv(1024)
			localizationResult = localizationResult.decode('ascii')
			receivedAcknowledge = "Received"
			zedBoardClientSocket.send(receivedAcknowledge.encode('ascii'))
			loResultArray = re.findall("[^,]+",localizationResult)
			with lock:
				(pos_x,pos_y,pos_z) = float(loResultArray[1]),float(loResultArray[2]),float(loResultArray[3])
			print ("Localization Data :: X:",pos_x," Y:",pos_y," Z:",pos_z)
		else:
			print ("Unidentified Data Identifier: ", dataIdentifier)
	
def mobilePhoneTransaction():
	while True:
		time.sleep(1)
		with lock:
			#Update objects with latest variable values
			mySignBoardData.isSignBoardDetected = signBoardValue
			myTextureData.texture = terrainValue
			myTextureData.pothole = potHoleVar
			myFaceDetectionData.noOfFaces = noOfFaces
			myFaceDetectionData.nameArray = nameArray
			myPositionInfo.pos_x = pos_x
			myPositionInfo.pos_y = pos_y
			myPositionInfo.pos_z = pos_z
		myConsolidatedString.signBoardString = json.dumps(mySignBoardData.__dict__)
		myConsolidatedString.textureString = json.dumps(myTextureData.__dict__)
		myConsolidatedString.faceDetectionString = json.dumps(myFaceDetectionData.__dict__)
		myConsolidatedString.positionString = json.dumps(myPositionInfo.__dict__)
		#print (mySignBoardData.__dict__)
		#print (myTextureData.__dict__)
		#print (myFaceDetectionData.__dict__)
		#print (myPositionInfo.__dict__)
		print (myConsolidatedString.__dict__)

def createServerForZedBoard():
	global zedBoardClientSocket
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

#Dictionary containing Label to Name mapping
LabelToName = {"Label1":"Name1","Label2":"Name2","LabelUnknown":"Unknown"}

## Main Execution Flow Starts here
createServerForZedBoard()
#createServerForMobileApp()

signBoardProcessThread = threading.Thread(target=signBoardProcess)
textureDetectProcessThread = threading.Thread(target=textureDetectProcess)
zedBoardTransactionThread = threading.Thread(target=zedBoardTransaction)
mobilePhoneTransactionThread = threading.Thread(target=mobilePhoneTransaction)
imageCaptureThread = threading.Thread(target=imageCaptureFromVideo)
signBoardProcessThread.daemon = True
textureDetectProcessThread.daemon = True
zedBoardTransactionThread.daemon = True
mobilePhoneTransactionThread.daemon = True
imageCaptureThread.daemon = True

#Initial Values for Shared Variables
pos_x = ""
pos_y = ""
pos_z = ""

noOfFaces = 0
labelArray = []
nameArray = []

terrainValue = [[0 for x in range(3)] for x in range(3)]
potHoleVar = "False"

signBoardValue = "False"

#Initial Object Definitions
mySignBoardData = SignBoardDetect(signBoardValue)
myTextureData = TextureDetect(terrainValue,potHoleVar)
myFaceDetectionData = FaceDetection(noOfFaces,nameArray)
myPositionInfo = PositionInfo(pos_x,pos_y,pos_z)
myConsolidatedString = ConsolidatedString("","","","")

imageCaptureThread.start()
signBoardProcessThread.start()
textureDetectProcessThread.start()
zedBoardTransactionThread.start()
mobilePhoneTransactionThread.start()
time.sleep(5.1)
