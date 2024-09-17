import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BOARD)

class ShiftRegister():
    def __init__(self, ser_pin, srclk_pin, rclk_pin, size=8):
        self.ser_pin = ser_pin
        self.srclk_pin = srclk_pin
        self.rclk_pin = rclk_pin
        self.size = size

        GPIO.setup(self.ser_pin, GPIO.OUT)
        GPIO.setup(self.srclk_pin, GPIO.OUT)
        GPIO.setup(self.rclk_pin, GPIO.OUT)

        GPIO.output(self.srclk_pin, GPIO.LOW)
        GPIO.output(self.rclk_pin, GPIO.LOW)

    def write(self, data):
        """Writes data into the shift register, with the MSB first and no respect for the length of the data.
        i.e. the entire register will be filled with the lowest "size" bits of data.

        Args:
            data (int): The data to be written into the shift register
        """
        GPIO.output(self.rclk_pin, GPIO.LOW)
        for i in range(self.size):
            GPIO.output(self.ser_pin, (data >> i) & 1)
            time.sleep(0.001)
            GPIO.output(self.srclk_pin, GPIO.HIGH)
            time.sleep(0.001)
            GPIO.output(self.srclk_pin, GPIO.LOW)
            time.sleep(0.001)
            
        GPIO.output(self.rclk_pin, GPIO.HIGH)
        time.sleep(0.001)
        GPIO.output(self.rclk_pin, GPIO.LOW)

    def cleanup(self):
        GPIO.cleanup()
