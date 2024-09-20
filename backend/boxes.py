import shift_register
import time

class Boxes():
    def __init__(self, num_boxes, ser_pin, srclk_pin, rclk_pin):
        self.ser_pin = ser_pin
        self.srclk_pin = srclk_pin
        self.rclk_pin = rclk_pin
        self.num_boxes = num_boxes

        self.sr = shift_register.ShiftRegister(self.ser_pin, self.srclk_pin, self.rclk_pin, num_boxes)
        self.deactivate_all() # Ensure that no boxes just pop open randomly

    def deactivate_all(self):
        # Bitshifts a 1 from bit 0 to the number of boxes, then subtracts 1 to make everything below 1
        # then writes that to the shift register
        self.sr.write((1 << self.num_boxes) - 1)

    def open_box(self, box_num):
        if box_num < 0:
            raise ValueError("Box number must be greater than or equal to 0")
        if box_num >= self.num_boxes:
            raise ValueError(f"Box number must be less than the number of boxes ({self.num_boxes})")
        
        all_deactivated = (1 << self.num_boxes) - 1
        box_activated = (1 << box_num) ^ all_deactivated # Bitshifts a 1 from bit 0 to the desired box number, then XORs it with all_deactivated
        
        self.sr.write(box_activated) # Bitshifts a 1 from bit 0 to the desired box number
        print(time.time())
        time.sleep(0.5) # Wait long enough for the solenoid to open fully
        print(time.time())
        self.deactivate_all() # Deactivate all boxes

    def cleanup(self):
        self.sr.cleanup()