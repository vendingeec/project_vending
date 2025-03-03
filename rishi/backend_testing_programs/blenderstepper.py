import time
import RPi.GPIO as GPIO

# Stepper motor control pins (example)
STEP_PIN = 26  # Stepper motor step pin
DIR_PIN = 19   # Stepper motor direction pin

# Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(STEP_PIN, GPIO.OUT)
GPIO.setup(DIR_PIN, GPIO.OUT)

# Function to move stepper motor
def move_stepper(steps, direction, step_delay=0.001):
    GPIO.output(DIR_PIN, direction)  # Set direction
    for _ in range(steps):
        GPIO.output(STEP_PIN, GPIO.HIGH)
        time.sleep(step_delay)  # Adjust speed here
        GPIO.output(STEP_PIN, GPIO.LOW)
        time.sleep(step_delay)  # Adjust speed here

# Main program
if __name__ == "__main__":
    try:
        # Move stepper motor forward (2000 steps)
        print("Moving stepper motor forward.")
        move_stepper(20000, GPIO.LOW)  # Forward direction
        time.sleep(1)

        

        print("Stepper motor movement completed.")
    
    except KeyboardInterrupt:
        print("Exiting program.")
    finally:
        GPIO.cleanup()  # Clean up GPIO pins
