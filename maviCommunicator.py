#! python3
import socket
import time
import threading
import subprocess
import re
import json
import cv2
import bluetooth
import sys
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

	valueLog = ["False","False","False"]
	localCount = 0
	while True:
		time.sleep(1)	#To be reviewed by Dedeepya
		with lock:	#So that image is not being read/written
			signBoardProgram = subprocess.Popen(["./signBoardDetect currentColorFrame.jpg"],stdout=subprocess.PIPE, shell = True)
			(tempSignBoardValue,err) = signBoardProgram.communicate()
			tempSignBoardValue = tempSignBoardValue.decode("utf-8").strip()
		if (localCount < 2):
			localCount +=1
			valueLog[localCount] = tempSignBoardValue
		else:
			localCount = 0
			valueLog[localCount] = tempSignBoardValue
		if (valueLog[0] == "True" and valueLog[1] == "True" and valueLog[2] == "True"):
			with lock:
				signBoardValue = "True"
		else:
			with lock:
				signBoardValue = "False"
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
			#textureDetectProgram = subprocess.Popen(["./demoTextureDetect.sh currentColorFrame.jpg"],stdout=subprocess.PIPE, shell = True)
			textureDetectProgram = subprocess.Popen(["./textureDetect currentGrayscaleFrame.jpg"],stdout=subprocess.PIPE, shell = True)
			(textureOutput,err) = textureDetectProgram.communicate()
			textureDetectResult = re.findall("[^,]+",textureOutput.decode("utf-8").strip())
			for i in range(2):
				for j in range(3):
					terrainValue[i][j] = textureDetectResult[3*i + j + 1]
			potHoleVar = textureDetectResult[7]
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

##Function for Capturing the FaceDetection Data from ZedBoard
def faceDetectionTransaction():
	global noOfFaces
	global nameArray,labelArray
	global faceDetectionClientSocket
	global serversocketForFD
	global host
	global portForFaceDetection
	while True:
		time.sleep(1)
		dataIdentifier = faceDetectionClientSocket.recv(1024)
		dataIdentifier = dataIdentifier.decode('ascii')
		if dataIdentifier == "FaceDetectionTransmit":	#Munib to have code for receiving jpeg
			#Code for Sending JPEG
			print ("Identified as FaceDetection Image Request. Sending Image")
			with lock:
				jpegImage = "currentGrayscaleFrame.jpg"
				f = open(jpegImage,'rb')
				l = f.read(1024)
				while (l):
					faceDetectionClientSocket.send(l)
					l = f.read(1024)
				f.close()
				copyImageProcess = subprocess.Popen(["\cp currentGrayscaleFrame.jpg transferredGrayscaleFrame.jpg"],stdout=subprocess.PIPE, shell = True)
				(copyOutput,err) = copyImageProcess.communicate()
			print ("Image Sent. Closing Socket.")
			faceDetectionClientSocket.close()
			print ("Waiting for reconnection ..")
			faceDetectionClientSocket,faceDetectionClientAddr = serversocketForFD.accept()
		elif dataIdentifier == "FaceDetectionReceive":	#Munib
			##Code for Receiving Face Detection Results

			print ("Identified as FaceDetection Results")
			#Handshake for sending FD Data
			stringForFDDataRequest = "Send FD Data"
			faceDetectionClientSocket.send(stringForFDDataRequest.encode('ascii'))

			faceDetectionResult = faceDetectionClientSocket.recv(1024)
			faceDetectionResult = faceDetectionResult.decode('ascii')
			receivedAcknowledge = "Received"
			faceDetectionClientSocket.send(receivedAcknowledge.encode('ascii'))
			fdResultArray = re.findall("[^,]+",faceDetectionResult)
			noOfFaces_temp = fdResultArray[1]
			print ("FD Result Array : ",fdResultArray)
			
			faceCoordinates = []
			facesDetected = []
			for face in range(int(noOfFaces_temp)):
				print ("Face Value: ",face)
				faceCoordinates.append((fdResultArray[2+face*4],fdResultArray[3+face*4],fdResultArray[4+face*4],fdResultArray[5+face*4]))
				faceRecognitionProgram = subprocess.Popen(["./recognizeFace transferredGrayscaleFrame.jpg " + fdResultArray[2+face*4] + " " + fdResultArray[3+face*4] + " " + fdResultArray[4+face*4] + " " + fdResultArray[5+face*4]],stdout=subprocess.PIPE, shell = True)
				(faceRecognitionOutput,err) = faceRecognitionProgram.communicate()
				facesDetected.append(faceRecognitionOutput.decode("utf-8").strip())

			#To be modified code
			with lock:
				noOfFaces = noOfFaces_temp
				nameArray = facesDetected
		else:
			print ("Unidentified Data Identifier: ", dataIdentifier)
	
def localizationTransaction():
	global pos_x,pos_y,pos_z
	global localizationClientSocket
	global serversocketForLO
	global host
	global portForLocalization
	while True:
		time.sleep(1)
		dataIdentifierForLO = localizationClientSocket.recv(1024)
		dataIdentifierForLO = dataIdentifierForLO.decode('ascii')
		if dataIdentifierForLO == "Localization":	#Munib
			#Code for Handling Localization Data
			print ("Identified as location data")
			#Handshake for sending Localization Data
			stringForLODataRequest = "Send LO Data"
			localizationClientSocket.send(stringForLODataRequest.encode('ascii'))

			localizationResult = localizationClientSocket.recv(1024)
			localizationResult = localizationResult.decode('ascii')
			receivedAcknowledge = "Received"
			localizationClientSocket.send(receivedAcknowledge.encode('ascii'))
			loResultArray = re.findall("[^,]+",localizationResult)
			with lock:
				(pos_x,pos_y,pos_z) = float(loResultArray[1]),float(loResultArray[2]),float(loResultArray[3])
			print ("Localization Data :: X:",pos_x," Y:",pos_y," Z:",pos_z)
		else:
			print ("Unidentified Data Identifier: ", dataIdentifierForLO)


def mobilePhoneTransaction():
	global mobileBluetoothSock
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
		#myConsolidatedString.signBoardString = mySignBoardData.__dict__
		#myConsolidatedString.textureString = myTextureData.__dict__
		#myConsolidatedString.faceDetectionString = myFaceDetectionData.__dict__
		#myConsolidatedString.positionString = myPositionInfo.__dict__

		#print (mySignBoardData.__dict__)
		#print (myTextureData.__dict__)
		#print (myFaceDetectionData.__dict__)
		#print (myPositionInfo.__dict__)
		print ("Sending to Phone : ", json.dumps(myConsolidatedString.__dict__))
		mobileBluetoothSock.send(json.dumps(myConsolidatedString.__dict__))

def createServerForFaceDetection():
	global faceDetectionClientSocket
	global serversocketForFD
	global host
	global portForFaceDetection
	# create a socket object
	serversocketForFD = socket.socket(
		        socket.AF_INET, socket.SOCK_STREAM) 
	
	
	portForFaceDetection = 7891 
	
	# bind to the port
	serversocketForFD.bind((host, portForFaceDetection))                                  
	
	# queue up to 5 requests
	serversocketForFD.listen(5)                                           
	
	print ("Server running on ", host," Port: ",  portForFaceDetection, "for Face Detection")
	
	faceDetectionClientSocket,faceDetectionClientAddr = serversocketForFD.accept()
	print ("Got a connection from ",faceDetectionClientAddr)

def createServerForLocalization():
	global localizationClientSocket 
	global serversocketForLO
	global host
	global portForLocalization
	# create a socket object
	serversocketForLO = socket.socket(
		        socket.AF_INET, socket.SOCK_STREAM) 
	
	portForLocalization = 7892 
	
	# bind to the port
	serversocketForLO.bind((host, portForLocalization))                                  
	
	# queue up to 5 requests
	serversocketForLO.listen(5)                                           
	
	print ("Server running on ", host," Port: ",  portForLocalization, "for Localization")
	
	localizationClientSocket,localizationClientAddr = serversocketForLO.accept()
	print ("Got a connection from ",localizationClientAddr)

def createServerForMobileApp():
	global mobileBluetoothSock
	uuid = "446118f0-8b1e-11e2-9e96-0800200c9a66"
	service_matches = bluetooth.find_service( uuid = uuid )
	
	if len(service_matches) == 0:
	    print ("couldn't find the FooBar service")
	    sys.exit(0)
	
	first_match = service_matches[0]
	mobilePort = first_match["port"]
	mobileName = first_match["name"]
	mobileHost = first_match["host"]
	
	print ("Connecting to ",mobileName, "on host ",mobileHost)
	mobileBluetoothSock=bluetooth.BluetoothSocket( bluetooth.RFCOMM )
	mobileBluetoothSock.connect((mobileHost, mobilePort))
	print ("Connected to Mobile Phone.")

def imageCaptureFromUsb():
	cap = cv2.VideoCapture(2)
	while(True):
		# Capture frame-by-frame
		ret, colorFrame = cap.read()
		
		# Our operations on the frame come here
		grayFrame = cv2.cvtColor(colorFrame, cv2.COLOR_BGR2GRAY)
		
		# Display the resulting frame
		cv2.imshow('Camera_Stream',colorFrame)
		if cv2.waitKey(1) & 0xFF == ord('q'):
			break
	
		with lock:
			cv2.imwrite('currentColorFrame.jpg',colorFrame)
			cv2.imwrite('currentGrayscaleFrame.jpg',grayFrame)
		#print ("Images Updated")

	# When everything done, release the capture
	cap.release()
	cv2.destroyAllWindows()

signBoardProcessThread = threading.Thread(target=signBoardProcess)
textureDetectProcessThread = threading.Thread(target=textureDetectProcess)
faceDetectionTransactionThread = threading.Thread(target=faceDetectionTransaction)
localizationTransactionThread = threading.Thread(target=localizationTransaction)
mobilePhoneTransactionThread = threading.Thread(target=mobilePhoneTransaction)
imageCaptureThread = threading.Thread(target=imageCaptureFromVideo)

signBoardProcessThread.daemon = True
textureDetectProcessThread.daemon = True
faceDetectionTransactionThread.daemon = True
localizationTransactionThread.daemon = True
mobilePhoneTransactionThread.daemon = True
imageCaptureThread.daemon = True

#Dictionary containing Label to Name mapping
LabelToName = {"Label1":"Name1","Label2":"Name2","LabelUnknown":"Unknown"}

# Specify Host
host = socket.gethostname()    
#host = '192.168.1.1'

## Main Execution Flow Starts here
createServerForFaceDetection()
createServerForLocalization()
createServerForMobileApp()

#Initial Values for Shared Variables
pos_x = ""
pos_y = ""
pos_z = ""

noOfFaces = 0
labelArray = []
nameArray = []

terrainValue = [[0 for x in range(3)] for x in range(2)]
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
faceDetectionTransactionThread.start()
localizationTransactionThread.start()
mobilePhoneTransactionThread.start()
imageCaptureFromUsbThread.start()
while True:
	a=1
#time.sleep(5.1)
mobileBluetoothSock.close()
faceDetectionClientSocket.close()
localizationClientSocket.close()
