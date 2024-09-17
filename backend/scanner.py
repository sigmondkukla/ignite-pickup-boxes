import serial
import requests

ser = serial.Serial('COM9', 9600, 8, 'N', 1, timeout=None)

while True:
    readline = ser.readline().decode('utf-8')
    print(f"Scanned: {readline}")
    requests.post("http://localhost:5000/api/scan", json={"code": readline})

ser.close()