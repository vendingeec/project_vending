import RPi.GPIO as GPIO
import time

# Suppress GPIO warnings
GPIO.setwarnings(False)

# Setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(7, GPIO.OUT)
GPIO.output(7, GPIO.HIGH)  # Keep relay OFF initially

time.sleep(1)

# Turn relay ON
GPIO.output(7, GPIO.LOW)


# Cleanup GPIO before exiting
GPIO.cleanup()  # Frees up all pins including GPIO 15
