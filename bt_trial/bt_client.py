#!/usr/bin/python3
import time
import sys
import bluetooth

uuid = "446118f0-8b1e-11e2-9e96-0800200c9a66"
service_matches = bluetooth.find_service( uuid = uuid )

if len(service_matches) == 0:
    print ("couldn't find the FooBar service")
    sys.exit(0)

first_match = service_matches[0]
port = first_match["port"]
name = first_match["name"]
host = first_match["host"]

print ("connecting to ",name, "on host ",host)
sampleJson="{'textureString': '{\"texture\": [[0, 0, 0], [0, 0, 0]], \"pothole\": \"False\"}', 'signBoardString': '{\"isSignBoardDetected\": \"False\"}', 'positionString': '{\"pos_x\": \"1.231\", \"pos_z\": \"2.2\", \"pos_y\": \"3.4\"}', 'faceDetectionString': '{\"noOfFaces\": 1, \"nameArray\": [\"Anupam\"]}', 'animalDetectionString' : '{\"noOfAnimals\": 1, \"animalArray\": [\"Cow\"], \"directionArray\" : [\"left\"]}'}"

strings = [sampleJson for x in range(10)]
sock=bluetooth.BluetoothSocket( bluetooth.RFCOMM )
sock.connect((host, port))
for string in strings:
	sock.send(string)
	time.sleep(1)
        powerSwitches = sock.recv(1024)
        print(powerSwitches)
sock.close()
