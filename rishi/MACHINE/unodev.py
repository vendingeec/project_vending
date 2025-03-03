import time
from pyfirmata import Arduino, util

# Change 'COM3' to the port where your Arduino is connected (Linux/macOS: '/dev/ttyUSB0' or '/dev/ttyACM0')
board = Arduino('COM3')

# The built-in LED on Arduino Uno is connected to Pin 13
led_pin = 13

print("Blinking the built-in LED...")

while True:
    board.digital[led_pin].write(1)  # Turn LED ON
    time.sleep(1)  # Wait 1 second
    board.digital[led_pin].write(0)  # Turn LED OFF
    time.sleep(1)  # Wait 1 second
