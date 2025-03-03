import RPi.GPIO as GPIO
import time

# GPIO setup
SENSOR_PIN = 14 # Replace with your chosen GPIO pin
GPIO.setmode(GPIO.BCM)
GPIO.setup(SENSOR_PIN, GPIO.IN)

try:
    while True:
        if GPIO.input(SENSOR_PIN):
            print("Object detected!")
        else:
            print("No object detected.")
        time.sleep(0.1)
except KeyboardInterrupt:
    print("Exiting...")