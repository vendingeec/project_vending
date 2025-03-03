import RPi.GPIO as GPIO
import time

# Suppress GPIO warnings
GPIO.setwarnings(False)

# Setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(18, GPIO.OUT)
GPIO.output(18, GPIO.LOW)  # Keep relay OFF initially

time.sleep(1)

# Turn relay ON
GPIO.output(18, GPIO.HIGH)

time.sleep(1)  # Keep relay ON for 1 second

# Turn relay OFF
GPIO.output(18, GPIO.LOW)

# Cleanup GPIO before exiting
GPIO.cleanup()  # Frees up all pins including GPIO 15
