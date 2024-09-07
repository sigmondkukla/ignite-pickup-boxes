import RPi.GPIO as GPIO
import shift_register
import time

SER_PIN = 11
SRCLK_PIN = 13
RCLK_PIN = 15

sr = shift_register.ShiftRegister(SER_PIN, SRCLK_PIN, RCLK_PIN)

box_num = int(input("Enter the box number you want to open (0-7): "))
if box_num < 0 or box_num > 7:
    print("Invalid box number")
    exit()
sr.write(1 << box_num)
time.sleep(0.1)
sr.write(0)

GPIO.cleanup()