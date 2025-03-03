import RPi.GPIO as GPIO
import time

# Define GPIO pins
PUL = 26 # Pulse pin
DIR = 21 # Direction pin

# Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(PUL, GPIO.OUT)
GPIO.setup(DIR, GPIO.OUT)


# Define initial direction (change as needed)
INITIAL_DIRECTION = GPIO.HIGH  # Set to GPIO.LOW for the opposite direcZZZZZtion
GPIO.output(DIR, INITIAL_DIRECTION)  # Apply initial direction

# Function to rotate motor
def stepper_motor(steps, delay):
    for _ in range(steps):
        GPIO.output(PUL, GPIO.HIGH)
        time.sleep(delay)  # Control speed
        GPIO.output(PUL, GPIO.LOW)
        time.sleep(delay)

# Rotate motor using initial direction
print("Rotating Motor...")
stepper_motor(100, 0.00025)  

# Pause
time.sleep(0.5)

# Cleanup GPIO
GPIO.cleanup()
