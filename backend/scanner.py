import serial
import requests
import os

if (os.name == "nt"):
    ser = serial.Serial('COM9', 9600, 8, 'N', 1, timeout=None) # testing on windows
else:
    ser = serial.Serial('/dev/ttyACM0', 9600, 8, 'N', 1, timeout=None) # on raspberry pi

while True:
    readline = ser.readline().decode('utf-8')
    print(f"Scanned: {readline}")
    requests.post("http://localhost:5000/api/scan", json={"code": readline})

ser.close()