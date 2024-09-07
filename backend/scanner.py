import serial

ser = serial.Serial('COM9', 9600, 8, 'N', 1, timeout=None)

num_reads = 0

while True:
    readline = ser.readline().decode('utf-8')
    print(readline)
    num_reads += 1
    if num_reads == 3:
        break

ser.close()