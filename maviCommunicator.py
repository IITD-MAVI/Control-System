#!python3
import socket
import time
import threading

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

print ("Server running on ", host," Port: ",  port)
