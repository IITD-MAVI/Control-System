#! python3
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
strings = ("{'textureString': '{\"texture\": [[0, 0, 0], [0, 0, 0]], \"pothole\": \"False\"}', 'signBoardString': '{\"isSignBoardDetected\": \"False\"}', 'positionString': '{\"pos_x\": \"\", \"pos_z\": \"\", \"pos_y\": \"\"}', 'faceDetectionString': '{\"noOfFaces\": 0, \"nameArray\": []}'}","{'textureString': '{\"texture\": [[1, 1, 1], [1, 1, 1]], \"pothole\": \"False\"}', 'signBoardString': '{\"isSignBoardDetected\": \"True\"}', 'positionString': '{\"pos_x\": \"\", \"pos_z\": \"\", \"pos_y\": \"\"}', 'faceDetectionString': '{\"noOfFaces\": 0, \"nameArray\": []}'}","{'textureString': '{\"texture\": [[0, 0, 0], [0, 0, 0]], \"pothole\": \"False\"}', 'signBoardString': '{\"isSignBoardDetected\": \"False\"}', 'positionString': '{\"pos_x\": \"\", \"pos_z\": \"\", \"pos_y\": \"\"}', 'faceDetectionString': '{\"noOfFaces\": 2, \"nameArray\": []}'}")
sock=bluetooth.BluetoothSocket( bluetooth.RFCOMM )
sock.connect((host, port))
for string in strings:
	sock.send(string)
	time.sleep(1)
sock.close()
