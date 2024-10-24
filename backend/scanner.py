import serial
import requests
import os
import argparse

args = argparse.ArgumentParser()
args.add_argument("--port", type=str, default="COM9", help="Serial port to connect to")
port = args.parse_args().port

# if (os.name == "nt"):
#     ser = serial.Serial('COM9', 9600, 8, 'N', 1, timeout=None) # testing on windows
# else:
#     ser = serial.Serial('/dev/ttyACM0', 9600, 8, 'N', 1, timeout=None) # on raspberry pi

ser = serial.Serial(port, 9600, 8, 'N', 1, timeout=None)

print("Connected to serial port")

while True:
    readline = ser.readline().decode('utf-8').strip()

    if readline == "":
        continue

    # Ensure the code is the right type, then only keep the data
    if readline[0:3] != "P01":
        print(f"Invalid code: {readline}")
        continue
    code = readline[3:]
    print(f"Scanned: {code}")

    try:
        response = requests.post("http://localhost:5000/api/scan", json={"code": code}, timeout=1)
        print(response.json())
    except requests.exceptions.RequestException as e:
        print(f"Failed to send scan to server due to: {e}")

ser.close()