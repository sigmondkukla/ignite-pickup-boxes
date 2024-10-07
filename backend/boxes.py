# import shift_register
import time
import os

if os.name == "nt":
    import sys
    import fake_rpi
    sys.modules['RPi'] = fake_rpi.RPi
    sys.modules['RPi.GPIO'] = fake_rpi.RPi.GPIO
    import RPi.GPIO as GPIO
else:
    import RPi.GPIO as GPIO

class Boxes():
    def __init__(self, num_boxes, box_pins):
        self.num_boxes = num_boxes
        self.box_pins = box_pins

        GPIO.setmode(GPIO.BOARD)
        for pin in self.box_pins:
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, GPIO.HIGH) # relay board is active low

        # self.sr = shift_register.ShiftRegister(self.ser_pin, self.srclk_pin, self.rclk_pin, num_boxes)
        self.deactivate_all() # Ensure that no boxes just pop open randomly

    def deactivate_all(self):
        for pin in self.box_pins:
            GPIO.output(pin, GPIO.HIGH)

    def open_box(self, box_num):
        if box_num < 0:
            raise ValueError("Box number must be greater than or equal to 0")
        if box_num >= self.num_boxes:
            raise ValueError(f"Box number must be less than the number of boxes ({self.num_boxes})")
        
        GPIO.output(self.box_pins[box_num], GPIO.LOW)
        time.sleep(0.5)
        GPIO.output(self.box_pins[box_num], GPIO.HIGH)

    def cleanup(self):
        GPIO.cleanup()