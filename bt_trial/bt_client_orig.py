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
sock=bluetooth.BluetoothSocket( bluetooth.RFCOMM )
sock.connect((host, port))
sock.send("hello!")
sock.close()
