import serial
import requests
import os

if (os.name == "nt"):
    ser = serial.Serial('COM9', 9600, 8, 'N', 1, timeout=None) # testing on windows
else:
    ser = serial.Serial('/dev/ttyACM0', 9600, 8, 'N', 1, timeout=None) # on raspberry pi

print("Connected to serial port")

while True:
    readline = ser.readline().decode('utf-8')
    readline = readline.strip()
    print(f"Start: {readline[0:2]}")
    if readline[0:2] != "P01":
        print(f"Invalid code: {readline}")
        continue
    code = readline[2:]
    print(f"Scanned: {code}")
    try:
        response = requests.post("http://localhost:5000/api/scan", json={"code": readline}, timeout=1)
        print(response.json())
    except Exception as e:
        print("Failed to send scan to server")
        print(e)

ser.close()