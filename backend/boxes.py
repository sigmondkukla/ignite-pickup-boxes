# import shift_register
import time
import os
import serial  # for arduino-controlled boxes

GPIO = None  # default: GPIO not available unless successfully imported

if os.name == "nt":
    import sys
    import fake_rpi

    sys.modules["RPi"] = fake_rpi.RPi
    sys.modules["RPi.GPIO"] = fake_rpi.RPi.GPIO
    import RPi.GPIO as GPIO  # type: ignore
else:
    try:
        import RPi.GPIO as GPIO
    except ModuleNotFoundError:
        GPIO = None


class Boxes:  # boxes parent class
    def __init__(self, num_boxes):  # constructor method
        self.num_boxes = num_boxes
        self.deactivate_all()  # Ensure that no boxes just pop open randomly

    def deactivate_all(self):
        pass

    def open_box(self, box_num):
        pass

    def cleanup(self):
        pass


class ArduinoBoxes(Boxes):  # arduino-controlled boxes subclass
    def __init__(self, num_boxes, serial_port):  # constructor method for arduino-controlled boxes subclass
        super().__init__(num_boxes)  # call parent class constructor method
        self.serial_port = serial_port
        self.ser = serial.Serial(
            serial_port,
            9600,
            timeout=1,
            write_timeout=1
        )  # open serial port
        self.deactivate_all()  # Ensure that no boxes just pop open randomly

    def deactivate_all(self):
        pass  # we assume that the arduino will handle this case

    def _reopen_serial(self):
        try:
            if self.ser and self.ser.is_open:
                self.ser.close()
        except Exception:
            pass

        self.ser = serial.Serial(
            self.serial_port,
            9600,
            timeout=1,
            write_timeout=1
        )

    def open_box(self, box_num):
        if box_num < 0:
            raise ValueError("Box number must be greater than or equal to 0")
        if box_num >= self.num_boxes:
            raise ValueError(f"Box number must be less than the number of boxes ({self.num_boxes})")

        try:
            if not self.ser.is_open:
                self.ser.open()

            # send box number as a string followed by a newline character to the arduino
            self.ser.write(f"{box_num}\n".encode())
            self.ser.flush()

        except serial.SerialException:
            # Try reopening the port once, then resend command
            self._reopen_serial()
            self.ser.write(f"{box_num}\n".encode())
            self.ser.flush()

    def cleanup(self):
        try:
            if self.ser and self.ser.is_open:
                self.ser.close()  # close serial port
        except Exception:
            pass


class GPIOBoxes(Boxes):  # GPIO-controlled boxes subclass
    def __init__(self, num_boxes, box_pins):
        if GPIO is None:
            raise RuntimeError("RPi.GPIO not available. Use ArduinoBoxes (USB) instead.")

        self.num_boxes = num_boxes
        self.box_pins = box_pins

        GPIO.setmode(GPIO.BOARD)
        for pin in self.box_pins:
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, GPIO.HIGH)  # relay board is active low

        # self.sr = shift_register.ShiftRegister(self.ser_pin, self.srclk_pin, self.rclk_pin, num_boxes)
        self.deactivate_all()  # Ensure that no boxes just pop open randomly

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
